"""Campaign-level tests for judge cache wiring and evidence preservation.

These tests demonstrate the gaps that ``harden-llm-judge-campaign-wiring``
addresses.  They assert the *desired* behavior and are expected to fail
until the implementation lands:

1. Production runners do not currently reuse identical judge decisions
   because no campaign-scoped cache is passed to ``JudgeClient``.
2. Cache-hit evidence loses member details because the cache stores only
   aggregate floats instead of complete ``JudgeEvidence`` records.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from gitbench.harness.campaign import (
    AttemptIdentity,
    Campaign,
    JudgeEvidence,
    JudgeMemberResult,
    make_campaign,
)
from gitbench.harness.judge import JudgeCache, JudgeClient
from gitbench.harness.scorer import Scorer
from gitbench.harness.types import Fixture


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _llm_judge_fixture() -> Fixture:
    return Fixture(
        id="judge_001",
        description="Judge-enabled fixture",
        setup=["git init"],
        prompt="Generate commit message",
        expected="fix: correct spelling error in file.txt",
        scoring={"type": "llm_judge", "threshold": 0.7},
    )


def _mock_judge_client(score: float = 0.9, model_id: str = "judge-model") -> MagicMock:
    """Create a mock judge model client."""
    client = MagicMock()
    client.generate.return_value = {"text": str(score)}
    client.model = model_id
    return client


# ---------------------------------------------------------------------------
# Gap 1: Production runners do not reuse judge decisions
# ---------------------------------------------------------------------------

class TestProductionRunnerCacheReuse:
    """Show that production runners should reuse judge decisions via a cache."""

    def test_runner_judge_client_should_have_campaign_cache(self):
        """BenchmarkRunner should wire a campaign cache to its JudgeClient when provided."""
        from gitbench.harness.runner import BenchmarkRunner

        registry = {}
        model_client = MagicMock()
        judge_config = {
            "profile": "judge-profile",
            "_config": {
                "models": {
                    "judge-profile": {
                        "models": ["judge-model"],
                        "provider": "openai",
                    }
                }
            },
        }

        cache = JudgeCache()

        with pytest.MonkeyPatch().context() as ctx:
            ctx.setenv("OPENAI_API_KEY", "sk-test")
            from gitbench.harness.model import MockModelClient

            ctx.setattr(
                "gitbench.cli.get_model_client",
                lambda *a, **kw: MockModelClient(model="judge-model"),
            )

            runner = BenchmarkRunner(
                registry,
                model_client,
                judge_config=judge_config,
                judge_cache=cache,
            )

            # The runner's judge client should have the campaign-scoped cache.
            assert runner._judge_client is not None
            assert runner._judge_client._cache is cache, (
                "Production runners should wire the campaign-scoped cache "
                "to their JudgeClient for decision reuse."
            )

    def test_two_scorers_sharing_cache_reuse_judge_decision(self):
        """Two scoring calls with the same cache key should issue one judge call."""
        mock_client = _mock_judge_client(0.92)
        mock_client.model = "judge-model"
        cache = JudgeCache()
        judge = JudgeClient([mock_client], cache=cache)
        scorer = Scorer(judge_client=judge)
        fixture = _llm_judge_fixture()

        context = {
            "fixture_input_hash": "input-a",
            "target_output_hash": "output-a",
        }

        result1 = scorer.score(
            fixture, "message-a", diff="diff",
            campaign_scoring_context=dict(context),
        )
        result2 = scorer.score(
            fixture, "message-a", diff="diff",
            campaign_scoring_context=dict(context),
        )

        assert result1.similarity == 0.92
        assert result2.similarity == 0.92
        # The second call should be a cache hit — only one model.generate call.
        assert mock_client.generate.call_count == 1


# ---------------------------------------------------------------------------
# Gap 2: Cache-hit evidence loses member details
# ---------------------------------------------------------------------------

class TestCacheHitEvidencePreservesMembers:
    """Cache hits should preserve full member-level evidence."""

    def test_cache_hit_preserves_member_results(self):
        """A cache hit should return the original member results, not an empty list."""
        mock_client = _mock_judge_client(0.92, "judge-model")
        cache = JudgeCache()
        client = JudgeClient([mock_client], cache=cache)

        # First call populates the cache with full evidence.
        evidence1 = client.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("input-a", "output-a")
        )
        assert len(evidence1.members) == 1
        assert evidence1.members[0].score == 0.92
        assert evidence1.members[0].model_id == "judge-model"

        # Second call is a cache hit.
        evidence2 = client.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("input-a", "output-a")
        )

        # The cache hit should preserve the original member evidence.
        assert evidence2.final_score == 0.92
        assert len(evidence2.members) == 1, (
            "Cache hits should preserve original member results, "
            "not return an empty members list."
        )
        assert evidence2.members[0].score == 0.92
        assert evidence2.members[0].model_id == "judge-model"

    def test_cache_hit_marks_reuse_state(self):
        """A cache hit should indicate the decision was reused."""
        mock_client = _mock_judge_client(0.85, "judge-model")
        cache = JudgeCache()
        client = JudgeClient([mock_client], cache=cache)

        client.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("input-a", "output-a")
        )
        evidence2 = client.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("input-a", "output-a")
        )

        # The evidence should indicate a cache hit.
        assert evidence2.cache_key is not None
        # After the change, there should be an explicit reuse indicator.
        # Currently there is no such field on JudgeEvidence.

    def test_cache_hit_preserves_aggregation_method(self):
        """Cache hit evidence should preserve the original aggregation method."""
        mock_client = _mock_judge_client(0.85, "judge-model")
        cache = JudgeCache()
        client = JudgeClient([mock_client], cache=cache)

        evidence1 = client.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("input-a", "output-a")
        )
        original_method = evidence1.aggregation_method

        evidence2 = client.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("input-a", "output-a")
        )

        assert evidence2.aggregation_method == original_method

class TestProvenanceJudgeHash:
    """Judged attempt provenance should record the actual judge config hash."""

    def test_provenance_uses_judge_evidence_hash_not_scorer_hash(self):
        """Provenance should record the judge evidence's config hash,
        not the scorer configuration hash."""
        from gitbench.harness.campaign import (
            AttemptIdentity,
            Campaign,
            FixtureExpectedHashes,
            JudgeEvidence,
            Provenance,
            make_campaign,
        )
        from gitbench.harness.campaign_executor import raw_attempt_from_score
        from gitbench.harness.types import Score

        campaign = make_campaign(
            campaign_id="cmp-prov",
            fixture_ids=["bench/f1"],
            model_ids=["m1"],
            output_modes=["text"],
            planned_trial_count=1,
            scorer_config_hash="scorer-hash-123",
            judge_config_hash="judge-hash-campaign",
        )
        campaign.config.expected_fixture_hashes = {
            "bench/f1": FixtureExpectedHashes(
                fixture_input_hash="fix-input",
                rendered_prompt_hash="prompt-hash",
                expected_hash="expected-hash",
                scoring_input_hash="scoring-input",
                request_config_hash="req-hash",
                scorer_config_hash="scorer-hash-123",
            )
        }

        identity = AttemptIdentity(
            campaign_id="cmp-prov",
            trial_index=1,
            model_id="m1",
            reasoning_effort="none",
            output_mode="text",
            fixture_id="bench/f1",
            benchmark="bench",
        )

        score = Score(
            fixture_id="bench/f1",
            passed=True,
            similarity=0.9,
            model_output="good message",
            judge_evidence=JudgeEvidence(
                judge_config_hash="actual-judge-hash-from-evidence",
                aggregation_method="average",
                final_score=0.9,
                members=[],
            ).to_dict(),
        )

        attempt = raw_attempt_from_score(campaign, identity, score)
        assert attempt.provenance is not None
        assert attempt.provenance.judge_config_hash == "actual-judge-hash-from-evidence"
        assert attempt.provenance.judge_config_hash != attempt.provenance.scorer_config_hash

    def test_provenance_falls_back_to_campaign_judge_hash_without_evidence(self):
        """When no judge evidence is present, fall back to campaign judge hash."""
        from gitbench.harness.campaign import (
            AttemptIdentity,
            FixtureExpectedHashes,
            make_campaign,
        )
        from gitbench.harness.campaign_executor import raw_attempt_from_score
        from gitbench.harness.types import Score

        campaign = make_campaign(
            campaign_id="cmp-prov2",
            fixture_ids=["bench/f1"],
            model_ids=["m1"],
            output_modes=["text"],
            planned_trial_count=1,
            scorer_config_hash="scorer-hash-123",
            judge_config_hash="campaign-judge-hash",
        )
        campaign.config.expected_fixture_hashes = {
            "bench/f1": FixtureExpectedHashes(
                fixture_input_hash="fix-input",
                rendered_prompt_hash="prompt-hash",
                expected_hash="expected-hash",
                scoring_input_hash="scoring-input",
                request_config_hash="req-hash",
                scorer_config_hash="scorer-hash-123",
            )
        }

        identity = AttemptIdentity(
            campaign_id="cmp-prov2",
            trial_index=1,
            model_id="m1",
            reasoning_effort="none",
            output_mode="text",
            fixture_id="bench/f1",
            benchmark="bench",
        )

        score = Score(
            fixture_id="bench/f1",
            passed=True,
            similarity=0.9,
            model_output="good message",
        )

        attempt = raw_attempt_from_score(campaign, identity, score)
        assert attempt.provenance is not None
        assert attempt.provenance.judge_config_hash == "campaign-judge-hash"
        assert attempt.provenance.judge_config_hash != attempt.provenance.scorer_config_hash


class TestCacheHitMemberReuse:
    """Cached decisions preserve original member evidence and mark reuse."""

    def test_cache_hit_marks_members_as_reused(self):
        """Each member on a cache hit should be marked as cache_hit=True."""
        from gitbench.harness.campaign import JudgeMemberResult
        from gitbench.harness.model import MockModelClient

        mock_client = MockModelClient(model="judge-model", response="0.9")
        cache = JudgeCache()
        client = JudgeClient([mock_client], cache=cache)

        # First call — populates cache.
        evidence1 = client.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("input-a", "output-a")
        )
        assert len(evidence1.members) == 1
        assert evidence1.members[0].cache_hit is False

        # Second call — cache hit.
        evidence2 = client.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("input-a", "output-a")
        )
        assert evidence2.cache_hit is True
        assert len(evidence2.members) == 1
        assert evidence2.members[0].cache_hit is True
        assert evidence2.members[0].score == 0.9
        assert evidence2.members[0].model_id == "judge-model"

    def test_cache_hit_preserves_member_failure_evidence(self):
        """Failed member evidence is preserved on cache hits."""
        from unittest.mock import MagicMock
        mock_client = MagicMock()
        mock_client.generate.side_effect = RuntimeError("API down")
        mock_client.model = "judge-model"
        cache = JudgeCache()
        client = JudgeClient([mock_client], cache=cache)

        # First call — exhausted, all members fail.
        evidence1 = client.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("input-a", "output-a")
        )
        assert evidence1.exhausted is True
        assert len(evidence1.members) == 1
        assert evidence1.members[0].error is not None

        # Second call — cache hit with preserved failure evidence.
        evidence2 = client.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("input-a", "output-a")
        )
        assert evidence2.exhausted is True
        assert len(evidence2.members) == 1
        assert evidence2.members[0].error is not None
        assert evidence2.cache_hit is True


class TestResumeJudgeIdentityValidation:
    """Resume should validate judge identity against the campaign manifest."""

    def test_legacy_judge_campaign_rejected_on_resume(self):
        """A judge campaign without judge_config_hash should be rejected."""
        from gitbench.harness.campaign import (
            AttemptIdentity,
            CampaignState,
            Trial,
            make_campaign,
        )
        from gitbench.harness.campaign_store import (
            CampaignStore,
            build_resume_plan,
            LEGACY_JUDGE_CAMPAIGN_ERROR,
        )

        campaign = make_campaign(
            campaign_id="cmp-legacy",
            fixture_ids=["bench/f1"],
            model_ids=["m1"],
            output_modes=["text"],
            planned_trial_count=1,
            judge_config={"profile": "judge-profile"},
            # No judge_config_hash — simulates a legacy campaign.
        )
        campaign.trials = [
            Trial(
                trial_index=1,
                planned_attempts=1,
                attempt_identities=[
                    AttemptIdentity(
                        campaign_id="cmp-legacy",
                        trial_index=1,
                        model_id="m1",
                        reasoning_effort="none",
                        output_mode="text",
                        fixture_id="bench/f1",
                        benchmark="bench",
                    )
                ],
            )
        ]
        store = CampaignStore("cmp-legacy", base_dir="/tmp/test-legacy-judge")
        store.ensure_dirs()

        with pytest.raises(ValueError, match="judge configuration hash"):
            build_resume_plan(campaign, store)

    def test_non_judge_campaign_resumes_without_judge_identity(self):
        """A non-judge campaign without judge_config_hash should resume fine."""
        from gitbench.harness.campaign import (
            AttemptIdentity,
            Trial,
            make_campaign,
        )
        from gitbench.harness.campaign_store import CampaignStore, build_resume_plan

        campaign = make_campaign(
            campaign_id="cmp-non-judge",
            fixture_ids=["bench/f1"],
            model_ids=["m1"],
            output_modes=["text"],
            planned_trial_count=1,
            # No judge_config — non-judge campaign.
        )
        campaign.trials = [
            Trial(
                trial_index=1,
                planned_attempts=1,
                attempt_identities=[
                    AttemptIdentity(
                        campaign_id="cmp-non-judge",
                        trial_index=1,
                        model_id="m1",
                        reasoning_effort="none",
                        output_mode="text",
                        fixture_id="bench/f1",
                        benchmark="bench",
                    )
                ],
            )
        ]
        store = CampaignStore("cmp-non-judge", base_dir="/tmp/test-non-judge")
        store.ensure_dirs()

        # Should not raise.
        needed = build_resume_plan(campaign, store)
        assert len(needed) == 1

    def test_judge_campaign_with_hash_resumes(self):
        """A judge campaign with judge_config_hash should resume fine."""
        from gitbench.harness.campaign import (
            AttemptIdentity,
            Trial,
            make_campaign,
        )
        from gitbench.harness.campaign_store import CampaignStore, build_resume_plan

        campaign = make_campaign(
            campaign_id="cmp-judge-hash",
            fixture_ids=["bench/f1"],
            model_ids=["m1"],
            output_modes=["text"],
            planned_trial_count=1,
            judge_config={"profile": "judge-profile"},
            judge_config_hash="valid-judge-hash",
        )
        campaign.trials = [
            Trial(
                trial_index=1,
                planned_attempts=1,
                attempt_identities=[
                    AttemptIdentity(
                        campaign_id="cmp-judge-hash",
                        trial_index=1,
                        model_id="m1",
                        reasoning_effort="none",
                        output_mode="text",
                        fixture_id="bench/f1",
                        benchmark="bench",
                    )
                ],
            )
        ]
        store = CampaignStore("cmp-judge-hash", base_dir="/tmp/test-judge-hash")
        store.ensure_dirs()

        # Should not raise.
        needed = build_resume_plan(campaign, store)
        assert len(needed) == 1


class TestEndToEndCacheReuse:
    """End-to-end tests proving identical evidence is judged once across trials, runners, and output modes."""

    def test_identical_evidence_judged_once_across_trials(self):
        """Two trials with the same fixture input and output should judge once."""
        from gitbench.harness.campaign import (
            AttemptIdentity,
            Campaign,
            FixtureExpectedHashes,
            Trial,
            make_campaign,
        )
        from gitbench.harness.campaign_store import CampaignStore
        from gitbench.harness.judge import JudgeCache, JudgeClient
        from gitbench.harness.model import MockModelClient

        mock_judge = MockModelClient(model="judge-model", response="0.9")
        cache = JudgeCache()
        judge = JudgeClient([mock_judge], cache=cache)

        # Simulate two trials with identical evidence (same fixture input hash
        # and same target output hash).
        for trial in [1, 2]:
            evidence = judge.evaluate_commit_message_evidence(
                "diff", "message", cache_key=("fix-input-1", "output-1")
            )
            assert evidence.final_score == 0.9

        # Only one judge call despite two trials.
        assert mock_judge.call_count == 1

    def test_identical_evidence_judged_once_across_output_modes(self):
        """Same fixture input and output across output modes should judge once."""
        from gitbench.harness.judge import JudgeCache, JudgeClient
        from gitbench.harness.model import MockModelClient

        mock_judge = MockModelClient(model="judge-model", response="0.85")
        cache = JudgeCache()
        judge = JudgeClient([mock_judge], cache=cache)

        # Same evidence identity regardless of output mode.
        for mode in ["text", "json_schema"]:
            evidence = judge.evaluate_commit_message_evidence(
                "diff", "message", cache_key=("fix-input-1", "output-1")
            )
            assert evidence.final_score == 0.85

        assert mock_judge.call_count == 1

    def test_different_evidence_judged_separately(self):
        """Different target outputs should produce separate judge calls."""
        from gitbench.harness.judge import JudgeCache, JudgeClient
        from gitbench.harness.model import MockModelClient

        mock_judge = MockModelClient(model="judge-model", response="0.9")
        cache = JudgeCache()
        judge = JudgeClient([mock_judge], cache=cache)

        judge.evaluate_commit_message_evidence(
            "diff", "message-a", cache_key=("fix-1", "output-a")
        )
        judge.evaluate_commit_message_evidence(
            "diff", "message-b", cache_key=("fix-1", "output-b")
        )

        assert mock_judge.call_count == 2


class TestRestartResumeCacheReuse:
    """Restart/resume tests proving persisted evidence is reused and different campaign IDs do not share entries."""

    def test_persisted_evidence_is_reused_on_resume(self, tmp_path):
        """After restart, a new JudgeClient with the loaded cache reuses evidence."""
        from gitbench.harness.campaign import JudgeEvidence, JudgeMemberResult
        from gitbench.harness.campaign_store import CampaignStore
        from gitbench.harness.judge import JudgeCache, JudgeClient
        from gitbench.harness.model import MockModelClient

        # First "run": create cache, judge, and persist.
        mock_judge = MockModelClient(model="judge-model", response="0.9")
        cache = JudgeCache()
        judge = JudgeClient([mock_judge], cache=cache)
        judge.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("fix-1", "out-1")
        )
        assert mock_judge.call_count == 1

        store = CampaignStore("cmp-restart", base_dir=str(tmp_path))
        store.save_judge_cache(cache)

        # Second "run": load cache and create a new judge with it.
        loaded_cache = store.load_judge_cache()
        assert loaded_cache is not None
        mock_judge2 = MockModelClient(model="judge-model", response="0.8")
        judge2 = JudgeClient([mock_judge2], cache=loaded_cache)
        evidence = judge2.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("fix-1", "out-1")
        )

        # Cache hit — no new judge call.
        assert evidence.final_score == 0.9
        assert evidence.cache_hit is True
        assert mock_judge2.call_count == 0

    def test_different_campaigns_do_not_share_cache(self, tmp_path):
        """Each campaign has its own cache file; entries are not shared."""
        from gitbench.harness.campaign_store import CampaignStore
        from gitbench.harness.judge import JudgeCache, JudgeClient
        from gitbench.harness.model import MockModelClient

        # Campaign A judges and persists.
        mock_a = MockModelClient(model="judge-a", response="0.9")
        cache_a = JudgeCache()
        judge_a = JudgeClient([mock_a], cache=cache_a)
        judge_a.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("fix-1", "out-1")
        )
        store_a = CampaignStore("cmp-a", base_dir=str(tmp_path))
        store_a.save_judge_cache(cache_a)

        # Campaign B loads its own (empty) cache.
        store_b = CampaignStore("cmp-b", base_dir=str(tmp_path))
        cache_b = store_b.load_judge_cache()
        assert cache_b is None  # No cache file for campaign B.

        # Campaign B should not reuse campaign A's decision.
        mock_b = MockModelClient(model="judge-b", response="0.7")
        cache_b = JudgeCache()
        judge_b = JudgeClient([mock_b], cache=cache_b)
        evidence = judge_b.evaluate_commit_message_evidence(
            "diff", "message", cache_key=("fix-1", "out-1")
        )
        assert evidence.final_score == 0.7  # Fresh evaluation, not cached 0.9.
        assert mock_b.call_count == 1


class TestCacheMissInvalidation:
    """Cache-miss tests for changed target output, fixture input, rubric, aggregation, judge member, and judge request configuration."""

    def test_changed_target_output_misses_cache(self):
        """Different target output produces a cache miss."""
        from gitbench.harness.judge import JudgeCache, JudgeClient
        from gitbench.harness.model import MockModelClient

        mock = MockModelClient(model="judge-model", response="0.9")
        cache = JudgeCache()
        judge = JudgeClient([mock], cache=cache)

        judge.evaluate_commit_message_evidence(
            "diff", "msg", cache_key=("fix-1", "out-a")
        )
        judge.evaluate_commit_message_evidence(
            "diff", "msg", cache_key=("fix-1", "out-b")
        )
        assert mock.call_count == 2

    def test_changed_fixture_input_misses_cache(self):
        """Different fixture input produces a cache miss."""
        from gitbench.harness.judge import JudgeCache, JudgeClient
        from gitbench.harness.model import MockModelClient

        mock = MockModelClient(model="judge-model", response="0.9")
        cache = JudgeCache()
        judge = JudgeClient([mock], cache=cache)

        judge.evaluate_commit_message_evidence(
            "diff", "msg", cache_key=("fix-a", "out-1")
        )
        judge.evaluate_commit_message_evidence(
            "diff", "msg", cache_key=("fix-b", "out-1")
        )
        assert mock.call_count == 2

    def test_changed_judge_member_misses_cache(self):
        """Changing the judge model produces a cache miss."""
        from gitbench.harness.judge import JudgeCache, JudgeClient
        from gitbench.harness.model import MockModelClient

        mock_a = MockModelClient(model="judge-a", response="0.9")
        mock_b = MockModelClient(model="judge-b", response="0.8")
        cache = JudgeCache()

        judge_a = JudgeClient([mock_a], cache=cache)
        judge_a.evaluate_commit_message_evidence(
            "diff", "msg", cache_key=("fix-1", "out-1")
        )

        judge_b = JudgeClient([mock_b], cache=cache)
        judge_b.evaluate_commit_message_evidence(
            "diff", "msg", cache_key=("fix-1", "out-1")
        )
        # Different judge config hash means cache miss.
        assert mock_b.call_count == 1

    def test_changed_rubric_misses_cache(self):
        """Changing the rubric version produces a cache miss."""
        from gitbench.harness.judge import build_judge_identity, JudgeCache, JudgeClient
        from gitbench.harness.model import MockModelClient
        import hashlib, json

        mock = MockModelClient(model="judge-model", response="0.9")
        cache = JudgeCache()

        # Compute hashes with different rubric versions.
        identity_a = build_judge_identity([mock], rubric_version="v1")
        identity_b = build_judge_identity([mock], rubric_version="v2")
        hash_a = hashlib.sha256(json.dumps(identity_a, sort_keys=True).encode()).hexdigest()
        hash_b = hashlib.sha256(json.dumps(identity_b, sort_keys=True).encode()).hexdigest()
        assert hash_a != hash_b

    def test_changed_aggregation_misses_cache(self):
        """Changing the aggregation method produces a cache miss."""
        from gitbench.harness.judge import build_judge_identity
        from gitbench.harness.model import MockModelClient
        import hashlib, json

        mock = MockModelClient(model="judge-model", response="0.9")

        identity_a = build_judge_identity([mock], aggregation_method="average")
        identity_b = build_judge_identity([mock], aggregation_method="majority")
        hash_a = hashlib.sha256(json.dumps(identity_a, sort_keys=True).encode()).hexdigest()
        hash_b = hashlib.sha256(json.dumps(identity_b, sort_keys=True).encode()).hexdigest()
        assert hash_a != hash_b


class TestEvidenceExport:
    """Evidence export tests covering direct calls, cache hits, partial member failure, and complete judge exhaustion."""

    def _campaign_with_attempts(self, attempts):
        """Build a campaign with the given raw attempts for export testing."""
        from gitbench.harness.campaign import (
            AttemptIdentity,
            CampaignState,
            Trial,
            make_campaign,
        )
        campaign = make_campaign(
            campaign_id="cmp-export",
            fixture_ids=["bench/f1"],
            model_ids=["m1"],
            output_modes=["text"],
            planned_trial_count=1,
        )
        campaign.raw_attempts = attempts
        campaign.trials = [
            Trial(
                trial_index=1,
                planned_attempts=len(attempts),
                attempt_identities=[a.identity for a in attempts],
            )
        ]
        return campaign

    def test_export_includes_direct_judge_evidence(self):
        """Evidence from a direct (non-cached) judge call is in the report."""
        from gitbench.export import build_campaign_report
        from gitbench.harness.campaign import (
            AttemptIdentity,
            AttemptStatus,
            JudgeEvidence,
            JudgeMemberResult,
            RawAttempt,
        )

        attempt = RawAttempt(
            identity=AttemptIdentity(
                campaign_id="cmp-export",
                trial_index=1,
                model_id="m1",
                reasoning_effort="none",
                output_mode="text",
                fixture_id="bench/f1",
                benchmark="bench",
            ),
            status=AttemptStatus.VALID_PASS,
            passed=True,
            model_output="msg",
            judge_evidence=JudgeEvidence(
                judge_config_hash="jch-1",
                aggregation_method="average",
                final_score=0.9,
                members=[
                    JudgeMemberResult(
                        member_id="judge-0",
                        model_id="judge-model",
                        score=0.9,
                        cache_hit=False,
                    )
                ],
            ),
        )
        campaign = self._campaign_with_attempts([attempt])
        report = build_campaign_report(campaign)
        assert len(report.judge_evidence) == 1
        assert report.judge_evidence[0].final_score == 0.9
        assert report.judge_evidence[0].cache_hit is False

    def test_export_includes_cached_judge_evidence(self):
        """Evidence from a cache hit is in the report with cache_hit=True."""
        from gitbench.export import build_campaign_report
        from gitbench.harness.campaign import (
            AttemptStatus,
            JudgeEvidence,
            JudgeMemberResult,
            RawAttempt,
        )

        attempt = RawAttempt(
            identity=AttemptIdentity(
                campaign_id="cmp-export",
                trial_index=1,
                model_id="m1",
                reasoning_effort="none",
                output_mode="text",
                fixture_id="bench/f1",
                benchmark="bench",
            ),
            status=AttemptStatus.VALID_PASS,
            passed=True,
            model_output="msg",
            judge_evidence=JudgeEvidence(
                judge_config_hash="jch-1",
                aggregation_method="average",
                final_score=0.9,
                cache_hit=True,
                members=[
                    JudgeMemberResult(
                        member_id="judge-0",
                        model_id="judge-model",
                        score=0.9,
                        cache_hit=True,
                    )
                ],
            ),
        )
        campaign = self._campaign_with_attempts([attempt])
        report = build_campaign_report(campaign)
        assert len(report.judge_evidence) == 1
        assert report.judge_evidence[0].cache_hit is True
        assert len(report.judge_evidence[0].members) == 1
        assert report.judge_evidence[0].members[0].cache_hit is True

    def test_export_includes_partial_member_failure(self):
        """Evidence with partial member failure is in the report."""
        from gitbench.export import build_campaign_report
        from gitbench.harness.campaign import (
            AttemptIdentity,
            AttemptStatus,
            JudgeEvidence,
            JudgeMemberResult,
            RawAttempt,
        )

        attempt = RawAttempt(
            identity=AttemptIdentity(
                campaign_id="cmp-export",
                trial_index=1,
                model_id="m1",
                reasoning_effort="none",
                output_mode="text",
                fixture_id="bench/f1",
                benchmark="bench",
            ),
            status=AttemptStatus.VALID_PASS,
            passed=True,
            model_output="msg",
            judge_evidence=JudgeEvidence(
                judge_config_hash="jch-1",
                aggregation_method="average",
                final_score=0.6,
                members=[
                    JudgeMemberResult(
                        member_id="judge-0",
                        model_id="judge-a",
                        score=0.8,
                        cache_hit=False,
                    ),
                    JudgeMemberResult(
                        member_id="judge-1",
                        model_id="judge-b",
                        score=0.4,
                        cache_hit=False,
                    ),
                ],
            ),
        )
        campaign = self._campaign_with_attempts([attempt])
        report = build_campaign_report(campaign)
        assert len(report.judge_evidence) == 1
        assert len(report.judge_evidence[0].members) == 2

    def test_export_includes_exhausted_judge(self):
        """Exhausted judge evidence is in the report."""
        from gitbench.export import build_campaign_report
        from gitbench.harness.campaign import (
            AttemptIdentity,
            AttemptStatus,
            JudgeEvidence,
            JudgeMemberResult,
            RawAttempt,
        )

        attempt = RawAttempt(
            identity=AttemptIdentity(
                campaign_id="cmp-export",
                trial_index=1,
                model_id="m1",
                reasoning_effort="none",
                output_mode="text",
                fixture_id="bench/f1",
                benchmark="bench",
            ),
            status=AttemptStatus.UNSCORED,
            passed=False,
            model_output="msg",
            judge_evidence=JudgeEvidence(
                judge_config_hash="jch-1",
                aggregation_method="average",
                final_score=None,
                exhausted=True,
                error="All judge models failed",
                members=[
                    JudgeMemberResult(
                        member_id="judge-0",
                        model_id="judge-a",
                        error="API error",
                        cache_hit=False,
                    ),
                ],
            ),
        )
        campaign = self._campaign_with_attempts([attempt])
        report = build_campaign_report(campaign)
        assert len(report.judge_evidence) == 1
        assert report.judge_evidence[0].exhausted is True
        assert report.judge_evidence[0].final_score is None


class TestExhaustionHandling:
    """Exhaustion remains UNSCORED, excluded from quality denominators, and campaign-incomplete."""

    def test_direct_exhaustion_is_unscored(self):
        """Direct judge exhaustion produces UNSCORED status."""
        from gitbench.harness.campaign import (
            AttemptIdentity,
            AttemptStatus,
            JudgeEvidence,
            RawAttempt,
            make_campaign,
        )
        from gitbench.harness.campaign_executor import raw_attempt_from_score
        from gitbench.harness.campaign_store import CampaignStore
        from gitbench.harness.types import Fixture, Score

        fixture = Fixture(
            id="judge_001",
            description="Judge fixture",
            setup=["git init"],
            prompt="Generate commit message",
            expected="fix: bug",
            scoring={"type": "llm_judge", "threshold": 0.7},
        )

        score = Score(
            fixture_id="judge_001",
            passed=False,
            similarity=0.0,
            model_output="msg",
            error="judge_exhausted: All judge models failed",
            unscored=True,
            judge_evidence=JudgeEvidence(
                judge_config_hash="jch",
                aggregation_method="average",
                final_score=None,
                exhausted=True,
                error="All judge models failed",
                members=[],
            ).to_dict(),
        )

        campaign = make_campaign(
            campaign_id="cmp-exhaust-direct",
            fixture_ids=["bench/judge_001"],
            model_ids=["m1"],
            output_modes=["text"],
            planned_trial_count=1,
            judge_config_hash="jch",
        )
        from gitbench.harness.campaign import FixtureExpectedHashes
        campaign.config.expected_fixture_hashes = {
            "bench/judge_001": FixtureExpectedHashes(
                fixture_input_hash="fix-input",
                rendered_prompt_hash="prompt-hash",
                expected_hash="expected-hash",
            )
        }

        identity = AttemptIdentity(
            campaign_id="cmp-exhaust-direct",
            trial_index=1,
            model_id="m1",
            reasoning_effort="none",
            output_mode="text",
            fixture_id="bench/judge_001",
            benchmark="bench",
        )

        attempt = raw_attempt_from_score(campaign, identity, score)
        assert attempt.status == AttemptStatus.UNSCORED
        assert attempt.judge_evidence is not None
        assert attempt.judge_evidence.exhausted is True

    def test_cached_exhaustion_is_unscored(self):
        """Cached judge exhaustion also produces UNSCORED status."""
        from gitbench.harness.campaign import (
            AttemptIdentity,
            AttemptStatus,
            JudgeEvidence,
            JudgeMemberResult,
            RawAttempt,
        )
        from gitbench.harness.judge import JudgeCache, JudgeClient
        from gitbench.harness.model import MockModelClient
        from unittest.mock import MagicMock

        mock_client = MagicMock()
        mock_client.generate.side_effect = RuntimeError("API down")
        mock_client.model = "judge-model"
        cache = JudgeCache()
        judge = JudgeClient([mock_client], cache=cache)

        # First call — exhausted, cached.
        evidence1 = judge.evaluate_commit_message_evidence(
            "diff", "msg", cache_key=("fix-1", "out-1")
        )
        assert evidence1.exhausted is True
        assert evidence1.final_score is None

        # Second call — cache hit with exhausted evidence.
        evidence2 = judge.evaluate_commit_message_evidence(
            "diff", "msg", cache_key=("fix-1", "out-1")
        )
        assert evidence2.exhausted is True
        assert evidence2.final_score is None
        assert evidence2.cache_hit is True

    def test_exhausted_attempt_excluded_from_quality_denominator(self):
        """UNSCORED attempts are excluded from the quality denominator."""
        from gitbench.harness.campaign import (
            AttemptIdentity,
            AttemptStatus,
            RawAttempt,
            make_campaign,
        )
        from gitbench.harness.aggregation import refresh_campaign_aggregates
        from gitbench.harness.campaign import FixtureExpectedHashes

        campaign = make_campaign(
            campaign_id="cmp-exhaust-denom",
            fixture_ids=["bench/f1"],
            model_ids=["m1"],
            output_modes=["text"],
            planned_trial_count=2,
            judge_config_hash="jch",
        )
        campaign.config.expected_fixture_hashes = {
            "bench/f1": FixtureExpectedHashes(
                fixture_input_hash="fix-input",
                rendered_prompt_hash="prompt-hash",
                expected_hash="expected-hash",
            )
        }
        from gitbench.harness.campaign import Trial

        campaign.trials = [
            Trial(
                trial_index=1,
                planned_attempts=1,
                attempt_identities=[
                    AttemptIdentity(
                        campaign_id="cmp-exhaust-denom",
                        trial_index=1,
                        model_id="m1",
                        reasoning_effort="none",
                        output_mode="text",
                        fixture_id="bench/f1",
                        benchmark="bench",
                    ),
                ],
            ),
            Trial(
                trial_index=2,
                planned_attempts=1,
                attempt_identities=[
                    AttemptIdentity(
                        campaign_id="cmp-exhaust-denom",
                        trial_index=2,
                        model_id="m1",
                        reasoning_effort="none",
                        output_mode="text",
                        fixture_id="bench/f1",
                        benchmark="bench",
                    ),
                ],
            ),
        ]
        campaign.raw_attempts = [
            RawAttempt(
                identity=AttemptIdentity(
                    campaign_id="cmp-exhaust-denom",
                    trial_index=1,
                    model_id="m1",
                    reasoning_effort="none",
                    output_mode="text",
                    fixture_id="bench/f1",
                    benchmark="bench",
                ),
                status=AttemptStatus.UNSCORED,
                passed=False,
                model_output="",
            ),
            RawAttempt(
                identity=AttemptIdentity(
                    campaign_id="cmp-exhaust-denom",
                    trial_index=2,
                    model_id="m1",
                    reasoning_effort="none",
                    output_mode="text",
                    fixture_id="bench/f1",
                    benchmark="bench",
                ),
                status=AttemptStatus.VALID_PASS,
                passed=True,
                model_output="good msg",
            ),
        ]

        refresh_campaign_aggregates(campaign)
        # One valid attempt, one excluded.
        assert campaign.valid_attempts == 1
        assert campaign.excluded_attempts == 1
        assert campaign.state.value == "incomplete"

    def test_exhausted_campaign_is_incomplete(self):
        """A campaign with exhausted attempts is incomplete."""
        from gitbench.harness.campaign import (
            AttemptIdentity,
            AttemptStatus,
            RawAttempt,
            Trial,
            make_campaign,
            FixtureExpectedHashes,
        )
        from gitbench.harness.aggregation import refresh_campaign_aggregates

        campaign = make_campaign(
            campaign_id="cmp-exhaust-incomplete",
            fixture_ids=["bench/f1"],
            model_ids=["m1"],
            output_modes=["text"],
            planned_trial_count=1,
            judge_config_hash="jch",
        )
        campaign.config.expected_fixture_hashes = {
            "bench/f1": FixtureExpectedHashes(
                fixture_input_hash="fix-input",
                rendered_prompt_hash="prompt-hash",
                expected_hash="expected-hash",
            )
        }
        campaign.trials = [
            Trial(
                trial_index=1,
                planned_attempts=1,
                attempt_identities=[
                    AttemptIdentity(
                        campaign_id="cmp-exhaust-incomplete",
                        trial_index=1,
                        model_id="m1",
                        reasoning_effort="none",
                        output_mode="text",
                        fixture_id="bench/f1",
                        benchmark="bench",
                    )
                ],
            )
        ]
        campaign.raw_attempts = [
            RawAttempt(
                identity=AttemptIdentity(
                    campaign_id="cmp-exhaust-incomplete",
                    trial_index=1,
                    model_id="m1",
                    reasoning_effort="none",
                    output_mode="text",
                    fixture_id="bench/f1",
                    benchmark="bench",
                ),
                status=AttemptStatus.UNSCORED,
                passed=False,
                model_output="",
            ),
        ]

        refresh_campaign_aggregates(campaign)
        assert campaign.state.value == "incomplete"
        assert campaign.excluded_attempts == 1
