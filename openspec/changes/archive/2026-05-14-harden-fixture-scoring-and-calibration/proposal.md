## Why

GitBench fixtures currently mix robust state-based scoring with brittle text matching. Some valid answers fail because fixtures require one exact command spelling, while other suites appear too easy because broad similarity scoring accepts partial or incomplete answers.

This change hardens fixture scoring so correct equivalent answers pass, incorrect over-broad answers fail, and fixture difficulty better reflects the Git skill being measured.

## What Changes

- Add a generic, data-driven command equivalence scorer for fixtures that ask models to output Git commands.
- Allow fixture YAML to declare accepted single-command and multi-command alternatives without hardcoding Git-specific equivalence rules in Python.
- Normalize command output before comparison so insignificant whitespace and quoting differences do not cause failures.
- Fix known brittle or incorrect fixtures, including submodule listing accepting both `git submodule` and `git submodule status`, and the `git_show/f008` full-hash expectation.
- Tighten selection-style scoring so extra incorrect answers are penalized, not only missing expected answers.
- Audit all suites for overly permissive scoring, especially loose `similarity` thresholds on conflict-resolution fixtures.
- Add targeted harder fixtures or stronger assertions for suites with saturated pass rates.

## Capabilities

### New Capabilities

- `fixture-scoring-robustness`: Reusable scoring behavior for equivalent commands, normalized answers, and strict selection semantics.
- `fixture-calibration`: Requirements for auditing fixture difficulty, correcting brittle expectations, and strengthening suites that are too easy or too permissive.

### Modified Capabilities

<!-- None. Existing fixture metadata remains unchanged; this change introduces new scoring and calibration contracts. -->

## Impact

- **Fixture YAML files** (`fixtures/*/f*.yaml`): Some fixtures gain command equivalence configuration or corrected expectations.
- **`gitbench/harness/scorer.py`**: New generic scoring path for command equivalence and answer normalization.
- **Benchmark-specific scorers** (`gitbench/benchmarks/*.py`): Selection scorers may be tightened or migrated to reusable helpers.
- **Tests** (`tests/test_scorer.py`, `tests/test_benchmarks.py`, integration tests): New coverage for command equivalence, strict selection, and corrected fixture behavior.
- **Documentation** (`README.md`, `CONTRIBUTING.md`): Fixture authoring guidance for command equivalence and calibration expectations.
