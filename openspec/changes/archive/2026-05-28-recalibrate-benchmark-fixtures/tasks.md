## 1. Audit Baseline

- [x] 1.1 Add or document a repeatable query/report that ranks fixtures by pass rate, scoring type, benchmark, and representative failed outputs from `gitbench/web/data/gitbench.db`.
- [x] 1.2 Identify the current zero-pass fixtures and low-pass fixtures below the chosen audit threshold.
- [x] 1.3 Classify each audited low-pass fixture as setup defect, expected-value defect, scoring brittleness, prompt ambiguity, or genuine difficulty.

## 2. Deterministic Scorers

- [x] 2.1 Add `unordered_line_set` scoring with tests for reordered, missing, and extra lines.
- [x] 2.2 Add `numeric_exact` scoring with tests for whitespace, optional single-number prose normalization, and wrong-number failure.
- [x] 2.3 Add or extend dynamic commit-hash scoring for subject-selected short/full hash answers with repository-backed tests.
- [x] 2.4 Add semantic JSON structured-value scoring with tests for formatting differences, invalid JSON, and wrong values.
- [x] 2.5 Confirm existing scoring types remain compatible with their current tests.

## 3. Fixture Self-Checks

- [x] 3.1 Add fixture self-check coverage for static/non-hash expected values in hash-answer fixtures.
- [x] 3.2 Add fixture self-check coverage for multi-line exact-match fixtures that do not explicitly require order.
- [x] 3.3 Add fixture self-check coverage for Git-derived expected values where the expected answer can be computed from fixture setup.
- [x] 3.4 Wire self-checks into the relevant test suite or CLI validation path.

## 4. Zero-Pass Fixture Corrections

- [x] 4.1 Migrate `git_log_format/f002` to order-insensitive list scoring or explicitly require and validate the intended order.
- [x] 4.2 Migrate `git_log_format/f003` to order-insensitive list scoring or explicitly require and validate the intended order.
- [x] 4.3 Correct `git_log_format/f007` so the expected answer is derived as the short hash for `Fix null pointer bug`.
- [x] 4.4 Correct `git_log_format/f010` so merge setup creates the expected merge commits or the expected count matches actual repository state.

## 5. Low-Pass Fixture Corrections

- [x] 5.1 Verify and correct suspicious `git_grep` count/setup fixtures where common failed answers indicate expected-value mismatch.
- [x] 5.2 Review low-pass `rebase`, `cherry_pick`, and `merge_conflicts` fixtures for ambiguous conflict-resolution policy and update prompts/scoring deterministically.
- [x] 5.3 Review low-pass `blame_forensics` fixtures for expected-value correctness and prompt clarity before changing difficulty.
- [x] 5.4 Review low-pass `commit_squash` fixtures for scorer false positives on extra selected commits and tighten output instructions without accepting wrong selections.

## 6. Calibration And Documentation

- [x] 6.1 Re-run the relevant fixture tests and scorer tests after corrections.
- [x] 6.2 Recalibrate fixture difficulty labels after defect fixes using observed pass-rate bands plus documented manual review.
- [x] 6.3 Update fixture authoring documentation for the new deterministic scorers and self-check expectations.
- [x] 6.4 Bump the benchmark suite version to reflect scoring and fixture behavior changes.
