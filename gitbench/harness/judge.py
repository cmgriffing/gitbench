"""LLM judge client for evaluating free-form text outputs."""

import hashlib
import json
import logging
import re
import threading
from typing import Any

from gitbench.harness.campaign import JudgeEvidence, JudgeMemberResult
from gitbench.harness.model import ModelInterface
from gitbench.harness.types import ModelMessage

logger = logging.getLogger(__name__)

# Version constants for judge identity components.
JUDGE_RUBRIC_VERSION = "commit-message-rubric-v1"
JUDGE_AGGREGATION_METHOD = "average"
JUDGE_AGGREGATION_VERSION = "average-v1"

JUDGE_COMMIT_MESSAGE_PROMPT = """You are evaluating the quality of a commit message for a git diff.

First, review the original prompt given to the model:

<original_prompt>
{prompt}
</original_prompt>

Score the commit message on a scale from 0.0 to 1.0 based on:
- Does it accurately describe the changes in the diff?
- Is it concise and well-structured?
- Does it follow the instructions in the original prompt (length limits, format, etc.)?
- Does it contain ONLY the commit message (no reasoning, no extra commentary)?
- Does it follow conventional commit message format?
- Does it capture the intent and scope of the change?

Penalize heavily if the response includes reasoning, explanations, or anything
other than the requested commit message.

Return ONLY a number between 0.0 and 1.0. Do not include any explanation.

Git diff:
{diff}

Commit message:
{message}

Score:"""


def _extract_text(response) -> str:
    """Extract text from a model response (dict or string)."""
    if isinstance(response, dict):
        return response.get("text", response.get("content", ""))
    return str(response)


def _parse_score(text: str) -> float:
    """Parse a numeric score from the judge model response.

    Args:
        text: The raw response text from the judge model.

    Returns:
        A float between 0.0 and 1.0.

    Raises:
        ValueError: If no numeric score can be extracted.
    """
    match = re.search(r"(-?\d+(?:\.\d+)?)", text)
    if not match:
        raise ValueError(
            f"Judge response could not be parsed as a number: {text!r}"
        )

    score = float(match.group(1))
    if score < 0.0:
        score = 0.0
    elif score > 1.0:
        score = 1.0
    return score


def build_judge_identity(
    model_clients: list[ModelInterface],
    *,
    rubric_version: str = JUDGE_RUBRIC_VERSION,
    aggregation_method: str = JUDGE_AGGREGATION_METHOD,
    aggregation_version: str = JUDGE_AGGREGATION_VERSION,
) -> dict[str, Any]:
    """Build a canonical, secret-free judge identity structure.

    The identity includes every input that can change a judge decision:

    - Ordered judge members with model ID, provider type, reasoning level,
      and base URL.
    - The judge prompt / rubric version.
    - The aggregation algorithm and version.

    Credentials (API keys), transient capacity settings (timeout, retry
    count, attempt gates), and other non-decision inputs are excluded.
    """
    members: list[dict[str, Any]] = []
    for i, client in enumerate(model_clients):
        base_url = (
            getattr(client, "base_url", None)
            or getattr(client, "_base_url", None)
            or ""
        )
        # Provider type is inferred from the adapter class name.
        adapter_name = type(client).__name__
        members.append(
            {
                "index": i,
                "model_id": str(getattr(client, "model", None) or ""),
                "provider": adapter_name,
                "reasoning_level": str(
                    getattr(client, "reasoning_level", None) or ""
                ),
                "base_url": str(base_url or ""),
            }
        )
    return {
        "members": members,
        "rubric_version": rubric_version,
        "aggregation_method": aggregation_method,
        "aggregation_version": aggregation_version,
    }


def compute_judge_config_hash(model_clients: list[ModelInterface]) -> str:
    """Return a deterministic hash for the judge configuration.

    The hash is computed from the canonical, secret-free judge identity
    so that any decision-relevant change invalidates cached decisions.
    Credentials and transient capacity settings (timeout, retry count) are
    excluded.
    """
    identity = build_judge_identity(model_clients)
    canonical = json.dumps(identity, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class JudgeCache:
    """Campaign-scoped cache for LLM-judge decisions.

    Keys are tuples of ``(fixture_input_hash, target_output_hash,
    judge_config_hash)``.  Values store complete ``JudgeEvidence`` records
    so that repeated identical evaluations within a campaign reuse prior
    work without issuing duplicate judge calls and preserve full auditable
    member-level evidence on cache hits.

    Concurrent requests for the same evidence key are single-flight: the
    first caller evaluates the judge ensemble and later callers wait for
    and reuse the result.  Requests for different keys proceed
    independently.
    """

    def __init__(self) -> None:
        """Initialise an empty cache with single-flight coordination."""
        self._cache: dict[tuple[str, str, str], JudgeEvidence] = {}
        self._lock = threading.Lock()
        self._inflight: dict[tuple[str, str, str], threading.Event] = {}

    def get(
        self,
        fixture_input_hash: str,
        target_output_hash: str,
        judge_config_hash: str,
    ) -> JudgeEvidence | None:
        """Return cached evidence or ``None`` when not present.

        The returned evidence is a deep copy marked as a cache hit so
        that callers can distinguish reused decisions from fresh ones.
        """
        key = (fixture_input_hash, target_output_hash, judge_config_hash)
        with self._lock:
            evidence = self._cache.get(key)
        if evidence is None:
            return None
        # Return a copy marked as a cache hit, preserving original members.
        cached = JudgeEvidence.from_dict(evidence.to_dict())
        cached.cache_hit = True
        cached.cache_key = f"{fixture_input_hash}:{target_output_hash}:{judge_config_hash}"
        # Preserve original member evidence.
        cached.members = [
            JudgeMemberResult.from_dict(m.to_dict())
            for m in evidence.members
        ]
        for member in cached.members:
            member.cache_hit = True
        return cached

    def set(
        self,
        fixture_input_hash: str,
        target_output_hash: str,
        judge_config_hash: str,
        evidence: JudgeEvidence,
    ) -> None:
        """Store complete judge evidence in the campaign-scoped cache."""
        key = (fixture_input_hash, target_output_hash, judge_config_hash)
        with self._lock:
            self._cache[key] = evidence
            # Resolve any waiters for this key.
            event = self._inflight.pop(key, None)
        if event is not None:
            event.set()

    def acquire(
        self,
        fixture_input_hash: str,
        target_output_hash: str,
        judge_config_hash: str,
    ) -> bool:
        """Attempt to acquire single-flight ownership for an evidence key.

        Returns ``True`` when the caller is the first to request this key
        and should perform the judge evaluation.  Returns ``False`` when
        another caller is already evaluating this key; the caller should
        wait via :meth:`wait` and then check :meth:`get`.
        """
        key = (fixture_input_hash, target_output_hash, judge_config_hash)
        with self._lock:
            # Already cached?
            if key in self._cache:
                return False
            # Already in-flight?
            if key in self._inflight:
                return False
            # Claim ownership.
            self._inflight[key] = threading.Event()
            return True

    def wait(
        self,
        fixture_input_hash: str,
        target_output_hash: str,
        judge_config_hash: str,
        timeout: float = 300.0,
    ) -> bool:
        """Wait for an in-flight evaluation to complete.

        Returns ``True`` if the evaluation completed within the timeout,
        ``False`` otherwise.
        """
        key = (fixture_input_hash, target_output_hash, judge_config_hash)
        with self._lock:
            event = self._inflight.get(key)
        if event is None:
            return True  # No in-flight, already resolved.
        return event.wait(timeout=timeout)

    def resolve(
        self,
        fixture_input_hash: str,
        target_output_hash: str,
        judge_config_hash: str,
        evidence: JudgeEvidence | None = None,
    ) -> None:
        """Resolve an in-flight evaluation, storing evidence if provided.

        Always resolves waiters whether the evidence is a success, partial
        failure, or exhaustion.  When ``evidence`` is ``None``, waiters are
        released without caching (e.g. on unhandled error).
        """
        key = (fixture_input_hash, target_output_hash, judge_config_hash)
        with self._lock:
            if evidence is not None:
                self._cache[key] = evidence
            event = self._inflight.pop(key, None)
        if event is not None:
            event.set()

    def get_evidence_key(
        self,
        fixture_input_hash: str,
        target_output_hash: str,
        judge_config_hash: str,
    ) -> tuple[str, str, str]:
        """Return the evidence key tuple for external coordination."""
        return (fixture_input_hash, target_output_hash, judge_config_hash)

    def entries(self) -> dict[tuple[str, str, str], JudgeEvidence]:
        """Return a shallow copy of all cache entries for persistence."""
        return dict(self._cache)


class JudgeClient:
    """Wraps multiple model clients to evaluate free-form text outputs.

    The judge calls every model client in the profile and averages their
    scores. Each client is configured with ``retry_count=5`` and handles
    rate limiting via ``Retry-After`` headers internally.

    Only when *all* clients fail does the judge raise an error — which the
    Scorer catches and falls back to SequenceMatcher.
    """

    def __init__(
        self,
        model_clients: list[ModelInterface],
        *,
        cache: JudgeCache | None = None,
    ) -> None:
        """Initialise the judge client.

        Args:
            model_clients: One or more model adapters. Every client is
                called and their scores are averaged. Each should be
                configured with ``retry_count=5``.
            cache: Optional campaign-scoped judge cache. When provided,
                callers should supply a cache key to
                ``evaluate_commit_message`` to enable reuse.
        """
        if not model_clients:
            raise ValueError("JudgeClient requires at least one model client")
        self._model_clients = model_clients
        self._cache = cache
        self._config_hash = compute_judge_config_hash(model_clients)
        self._identity = build_judge_identity(model_clients)

    @property
    def config_hash(self) -> str:
        """Return the dedicated judge configuration hash."""
        return self._config_hash

    @property
    def judge_identity(self) -> dict[str, Any]:
        """Return the canonical, secret-free judge identity structure."""
        return dict(self._identity)

    def evaluate_commit_message(
        self,
        diff: str,
        message: str,
        prompt: str = "",
        *,
        cache_key: tuple[str, str] | None = None,
    ) -> float:
        """Evaluate a commit message and return the aggregated score.

        This is the backward-compatible thin wrapper around
        :meth:`evaluate_commit_message_evidence`.
        """
        evidence = self.evaluate_commit_message_evidence(
            diff, message, prompt=prompt, cache_key=cache_key
        )
        if evidence.final_score is None:
            raise ValueError(evidence.error or "Judge produced no usable score")
        return evidence.final_score

    def evaluate_commit_message_evidence(
        self,
        diff: str,
        message: str,
        prompt: str = "",
        *,
        cache_key: tuple[str, str] | None = None,
    ) -> JudgeEvidence:
        """Evaluate a commit message and return full member-level evidence.

        Args:
            diff: The git diff to evaluate against.
            message: The commit message generated by the model under test.
            prompt: The original prompt given to the model under test.
            cache_key: Optional cache key used with a campaign cache.

        Returns:
            A :class:`JudgeEvidence` object with member results, final
            aggregation, and failure state.

        Raises:
            ValueError: If all judge models fail.
        """
        if self._cache is not None and cache_key is not None:
            fixture_input_hash, target_output_hash = cache_key
            cached = self._cache.get(
                fixture_input_hash, target_output_hash, self._config_hash
            )
            if cached is not None:
                logger.debug(
                    "Judge cache hit for fixture input %s, output %s",
                    fixture_input_hash[:8],
                    target_output_hash[:8],
                )
                return cached

            # Single-flight: try to acquire ownership of this evidence key.
            if not self._cache.acquire(
                fixture_input_hash, target_output_hash, self._config_hash
            ):
                # Another caller is already evaluating this key — wait.
                logger.debug(
                    "Judge single-flight wait for fixture input %s, output %s",
                    fixture_input_hash[:8],
                    target_output_hash[:8],
                )
                self._cache.wait(fixture_input_hash, target_output_hash, self._config_hash)
                cached = self._cache.get(
                    fixture_input_hash, target_output_hash, self._config_hash
                )
                if cached is not None:
                    return cached
                # Wait timed out or owner failed without caching.
                # Fall through to perform our own evaluation.

        judge_prompt = JUDGE_COMMIT_MESSAGE_PROMPT.format(
            diff=diff, message=message, prompt=prompt
        )
        messages = [ModelMessage(role="user", content=judge_prompt)]

        # Track whether we acquired single-flight ownership so we can
        # always resolve waiters in a finally block.
        acquired_key: tuple[str, str, str] | None = None
        if self._cache is not None and cache_key is not None:
            fixture_input_hash, target_output_hash = cache_key
            with self._cache._lock:
                key = (fixture_input_hash, target_output_hash, self._config_hash)
                if key in self._cache._inflight:
                    acquired_key = key

        try:
            members: list[JudgeMemberResult] = []
            scores: list[float] = []

            for i, client in enumerate(self._model_clients):
                model_name = getattr(client, "model", f"client-{i}")
                member = JudgeMemberResult(
                    member_id=f"judge-{i}",
                    model_id=model_name,
                )
                try:
                    logger.debug(
                        "Judge calling model %d/%d (%s)",
                        i + 1,
                        len(self._model_clients),
                        model_name,
                    )
                    response = client.generate(messages)
                    text = _extract_text(response)
                    score = _parse_score(text)
                    scores.append(score)
                    member.score = score
                    member.passed = None  # Threshold is applied by the scorer.
                    logger.debug("Judge model '%s' scored %.2f", model_name, score)
                except Exception as exc:
                    logger.warning(
                        "Judge model '%s' failed (%d/%d): %s",
                        model_name,
                        i + 1,
                        len(self._model_clients),
                        exc,
                    )
                    member.error = str(exc)
                # Capture available provider-route provenance.
                member.provider_route_metadata = {
                    k: v
                    for k, v in {
                        "model_id": getattr(client, "model", None),
                        "reasoning_level": getattr(client, "reasoning_level", None),
                        "base_url": getattr(client, "base_url", None)
                        or getattr(client, "_base_url", None),
                    }.items()
                    if v is not None
                }
                members.append(member)

            evidence = JudgeEvidence(
                judge_config_hash=self._config_hash,
                aggregation_method="average",
                members=members,
            )

            if not scores:
                member_errors = "; ".join(
                    f"{m.member_id}: {m.error}" for m in members if m.error
                )
                evidence.error = (
                    f"All {len(self._model_clients)} judge model(s) failed. "
                    f"Errors: {member_errors}"
                )
                evidence.exhausted = True
                if self._cache is not None and cache_key is not None:
                    fixture_input_hash, target_output_hash = cache_key
                    self._cache.resolve(
                        fixture_input_hash, target_output_hash, self._config_hash, evidence
                    )
                return evidence

            average = sum(scores) / len(scores)
            logger.info(
                "Judge ensemble: %d/%d models returned scores, average=%.3f",
                len(scores),
                len(self._model_clients),
                average,
            )
            evidence.final_score = round(average, 4)
            if self._cache is not None and cache_key is not None:
                fixture_input_hash, target_output_hash = cache_key
                self._cache.resolve(
                    fixture_input_hash, target_output_hash, self._config_hash, evidence
                )
            return evidence
        except Exception:
            # Unexpected error - resolve waiters without caching so they
            # can fall through and evaluate independently.
            if acquired_key is not None:
                self._cache.resolve(acquired_key[0], acquired_key[1], acquired_key[2])
            raise
        finally:
            # Ensure waiters are always resolved even on unexpected exit.
            # resolve() is idempotent: if already resolved, the _inflight
            # entry is gone and this is a no-op.
            if acquired_key is not None:
                self._cache.resolve(acquired_key[0], acquired_key[1], acquired_key[2])

    def _extract_text(self, response) -> str:
        """Extract text from a model response (dict or string)."""
        return _extract_text(response)

    def _parse_score(self, text: str) -> float:
        """Parse a numeric score from the judge model response."""
        return _parse_score(text)
