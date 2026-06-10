## Why

Commit message generation scoring uses `difflib.SequenceMatcher` at a 0.5 threshold, which measures character-level overlap rather than semantic accuracy. Valid commit messages routinely fail because they use different wording than the single expected answer, while structurally similar but incorrect messages can pass. A secondary LLM judge can evaluate whether the message accurately describes the diff — the right dimension for this benchmark.

## What Changes

- Add a `judge` section to `gitbench.json` for configuring a judge model profile
- Add a `JudgeClient` that calls a separate (typically cheaper) model to evaluate commit message quality
- Modify the `Scorer` to accept an optional judge and use it for `commit_messages` benchmark fixtures
- Modify the `BenchmarkRunner` to wire a judge client into the scorer
- Replace `SequenceMatcher`-based similarity scoring with LLM judge scoring for `commit_messages` — judge produces a 0–1 score that feeds into `Score.similarity` and `passed = similarity >= threshold`
- Judge failures fall back to the existing scorer after one retry, marked as an error that `gitbench doctor` can rerun

## Capabilities

### New Capabilities

- **llm-judge-scoring**: An LLM-as-judge scoring mechanism that evaluates free-form text outputs (starting with commit messages) by asking a separate model whether the generated output accurately reflects the given context (diff, code, etc.)

### Modified Capabilities

None. This is a new mechanism that doesn't change existing spec-level requirements.

## Impact

- `gitbench.json`: New optional `judge` section
- `gitbench/harness/judge.py`: New module — `JudgeClient` class
- `gitbench/harness/scorer.py`: Modified — optional judge integration
- `gitbench/harness/runner.py`: Modified — wire judge into fixture execution
- `gitbench/benchmarks/commit_messages.py`: Modified — pass diff context to scorer for judge use
- `tests/`: New test file for judge client and updated scorer tests
