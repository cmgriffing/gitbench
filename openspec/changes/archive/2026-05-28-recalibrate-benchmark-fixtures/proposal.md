## Why

Recent benchmark data shows a small set of fixtures that no model passes and a larger set with unusually low pass rates. The failures are concentrated in brittle exact-match scoring, incorrect expected values, setup/prompt mismatches, and underspecified conflict-resolution policy rather than uniformly representing useful difficulty.

## What Changes

- Correct fixture defects that make valid answers fail, starting with the current zero-pass fixtures.
- Add deterministic scorers for answer shapes that should not require prose similarity or LLM judging.
- Migrate brittle fixtures to the appropriate deterministic scorer where valid equivalent answers are currently rejected.
- Add fixture self-checks that verify expected answers are consistent with the generated repository state.
- Recalibrate fixture difficulty labels from observed results after fixture and scoring corrections.
- Keep LLM-as-judge out of scope for this change.

## Capabilities

### New Capabilities

<!-- None. This change extends existing fixture calibration and scoring capabilities. -->

### Modified Capabilities

- `fixture-calibration`: Expand calibration requirements to cover current zero-pass/low-pass fixtures, fixture self-checks, and observed difficulty recalibration.
- `fixture-scoring-robustness`: Add deterministic scoring requirements for unordered line sets, numeric answers, dynamic commit hashes, and semantic structured values.

## Impact

- Fixture YAML files under `fixtures/*/f*.yaml`, especially `git_log_format`, `git_grep`, `rebase`, `cherry_pick`, `merge_conflicts`, `blame_forensics`, and `commit_squash`.
- Scoring code in `gitbench/harness/scorer.py` and benchmark-specific scorers such as `gitbench/benchmarks/commit_squash.py`.
- Fixture validation or audit tests under `tests/`.
- Documentation for fixture authoring and scoring guidance in `CONTRIBUTING.md` and/or `README.md`.
- Benchmark suite versioning, because fixture expectations and scoring behavior affect result comparability.
