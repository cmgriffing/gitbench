## Context

GitBench currently scores `commit_messages` benchmark outputs using `difflib.SequenceMatcher` with a 0.5 threshold. This measures character-level string similarity between the model's generated commit message and a single expected answer. The problem is semantic: many valid commit messages describe the same diff with different wording, and character similarity cannot distinguish between a valid alternative and an incorrect message.

The `gitbench.json` config already contains an `openrouter-llms-as-judges` profile with three cheap models (granite-4.1-8b, ling-2.6-flash, gpt-oss-120b) intended for this purpose. The infrastructure for calling arbitrary models already exists via `ModelInterface` and the OpenAI-compatible adapter.

## Goals / Non-Goals

**Goals:**
- Replace character-similarity scoring with LLM-based semantic evaluation for `commit_messages`
- Judge scoring is *required* for judge-applicable benchmarks — running without judge config exits with an error
- Judge produces a 0–1 float score that feeds directly into the existing `Score.similarity` field
- Judge model group is configured via a `judge` section in `gitbench.json` referencing a model profile
- Judge failures degrade gracefully to the existing scorer (after one retry), marked as an error
- Mechanism is designed to be extendable to other benchmarks (cherry_pick, merge_conflicts, rebase) in the future

**Non-Goals:**
- Judge scoring for benchmarks other than `commit_messages` (cherry_pick, merge_conflicts, rebase are recognized as future candidates but out of scope)
- Replacing scoring for `exact_match`, `state_assertions`, `command_equivalence`, or other deterministic scoring types
- Real-time judge scoring during parallel fixture execution (judge calls happen inline in the fixture thread)
- Changing the `Score` dataclass schema in a breaking way

## Decisions

### Decision 1: Judge configuration lives in `gitbench.json` under a top-level `judge` key

**Rationale:** The judge is orthogonal to the model-under-test profiles. It's a separate concern — a meta-evaluation layer. Keeping it at the config top level makes it discoverable and independent of which profiles are being tested.

**Alternative considered:** Judge configuration per-profile (e.g., `models.<profile>.judge`). Rejected because the same judge should apply across all profiles being tested — it's a benchmark setting, not a model setting.

```json
{
  "judge": {
    "profile": "openrouter-llms-as-judges"
  }
}
```

The judge applies to all benchmarks in `JUDGE_REQUIRED_BENCHMARKS` (currently `commit_messages`). No per-benchmark opt-in is needed — if a benchmark requires a judge, it gets one whenever the `judge` section is present.

### Decision 2: `JudgeClient` wraps a `ModelInterface` with a domain-specific evaluation method

**Rationale:** The judge is a thin wrapper around an existing `ModelInterface`. It doesn't need a new model client implementation — it reuses the OpenAI-compatible adapter. The value-add is the prompt construction and response parsing.

```python
class JudgeClient:
    def __init__(self, model_client: ModelInterface):
        ...
    
    def evaluate_commit_message(self, diff: str, message: str) -> float:
        """Returns 0.0–1.0 rating of how well the message describes the diff."""
```

**Alternative considered:** Judge as a separate `ModelInterface` implementation. Rejected — no new protocol needed. The existing OpenAI adapter already does what we need.

### Decision 3: Judge score replaces `SequenceMatcher` similarity in the scorer

**Rationale:** The `Scorer.score()` method currently computes `similarity` via `SequenceMatcher` for `similarity` type fixtures. For judge-enabled benchmarks, we bypass that and use the judge score instead. The `passed` field is still computed as `similarity >= threshold` — no change to the scoring contract.

```python
# In Scorer.score():
if scoring_type == "similarity" and self._judge_client is not None:
    similarity = self._judge_client.evaluate_commit_message(diff, model_output)
else:
    similarity = SequenceMatcher(None, model_output, expected).ratio()
```

**Alternative considered:** Augmenting with an additional `judge_score` field on `Score`. Rejected — keeps `similarity` as the authoritative score and avoids schema changes to `Score`. Simpler and more consistent.

### Decision 4: Judge prompt is constructed from the fixture's diff context, not hardcoded

**Rationale:** The `commit_messages` benchmark already produces a diff via `get_diff()` and formats a prompt via `format_prompt()`. The judge prompt is separate from the model prompt — it's a meta-prompt asking the judge model to evaluate. The scorer receives the diff alongside the model output.

The benchmark's `score()` method signature is already:
```python
def score(self, fixture, model_output, repo_path=None) -> Score
```

The `repo_path` gives access to the repo, and `fixture` gives access to the prompt and diff context. The judge needs the diff, which the benchmark already has from `get_diff()`.

### Decision 5: Judge calls all models in the profile and averages their scores

**Rationale:** Using an ensemble of judge models reduces individual model bias and produces a more robust score. Every model in the profile is called; individual model failures (after 5 adapter-level retries with ``Retry-After`` backoff) are excluded from the average. Only when every model fails does the system fall back to ``SequenceMatcher``.

## Risks / Trade-offs

- **[Cost]** Judge calls add API cost to every `commit_messages` fixture (12 calls per benchmark run). → Mitigation: The `openrouter-llms-as-judges` profile uses cheap models. 12 calls = pennies. Acceptable.
- **[Latency]** Judge calls add ~500ms–2s per fixture. → Mitigation: Judge calls happen inline during fixture execution, serializing after the model-under-test response. For 12 fixtures at 2s each = +24s max. Acceptable for a benchmark suite.
- **[Judge bias]** The judge model may have biases (preferring certain formats, penalizing valid but unusual messages). → Mitigation: Multiple judge models in the profile provide redundancy; could extend to majority-vote in the future. The prompt is structured with explicit scoring criteria to reduce subjectivity.
- **[Model availability]** Judge models may be unavailable or rate-limited. → Mitigation: 5 adapter-level retries per model with ``Retry-After`` backoff, plus model-level fallback across all models in the profile. Graceful fallback to ``SequenceMatcher`` as last resort.
