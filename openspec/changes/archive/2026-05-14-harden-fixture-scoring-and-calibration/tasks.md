## 1. Command Equivalence Scoring

- [x] 1.1 Add `command_equivalence` handling to `gitbench/harness/scorer.py`.
- [x] 1.2 Implement command normalization using blank-line removal, whitespace trimming, and `shlex.split()` token comparison.
- [x] 1.3 Support `accepted` alternatives as either single command strings or ordered command sequences.
- [x] 1.4 Return clear scoring errors when command output cannot be parsed or no accepted alternative matches.
- [x] 1.5 Add unit tests for single-command matches, equivalent alternatives, whitespace normalization, quote normalization, invalid syntax, multi-command sequences, and wrong command order.

## 2. Selection Scoring Tightening

- [x] 2.1 Update branch cleanup selection scoring so extra incorrect branches fail by default.
- [x] 2.2 Review commit selection scoring for missing/extra behavior and tighten pass criteria where extras are currently accepted.
- [x] 2.3 Add tests proving exact selections pass, missing selections fail, and extra selections fail.
- [x] 2.4 Preserve or explicitly document any fixture that intentionally allows partial credit.

## 3. Known Fixture Corrections

- [x] 3.1 Migrate `fixtures/submodule_usage/f006.yaml` to `command_equivalence` accepting both `git submodule` and `git submodule status`.
- [x] 3.2 Review related read-only command fixtures such as submodule status, `.gitmodules` viewing, and worktree listing for valid alternatives.
- [x] 3.3 Correct `fixtures/git_show/f008.yaml` so the full-hash prompt no longer expects the literal commit subject.
- [x] 3.4 Add or update tests that load and score the corrected fixtures.

## 4. Suite Calibration Audit

- [x] 4.1 Audit `blame_forensics`, `branch_cleanup`, `cherry_pick`, and `commit_messages` for brittle expectations, loose thresholds, and difficulty mismatches.
- [x] 4.2 Audit `commit_squash`, `git_bisect`, `git_clean`, and `git_grep` for brittle expectations, loose thresholds, and difficulty mismatches.
- [x] 4.3 Audit `git_log_format`, `git_show`, `merge_conflicts`, and `rebase` for brittle expectations, loose thresholds, and difficulty mismatches.
- [x] 4.4 Audit `reflog`, `stash_recovery`, `submodule_usage`, `tag_management`, and `worktree_usage` for brittle expectations, loose thresholds, and difficulty mismatches.
- [x] 4.5 For each audited suite, apply focused fixture corrections or note why no change is needed.

## 5. Conflict Fixture Hardening

- [x] 5.1 Identify conflict-resolution fixtures that describe multi-file resolution but score only one returned file.
- [x] 5.2 Migrate suitable conflict fixtures to structured or file-aware scoring, or explicitly narrow their prompts to the scored file.
- [x] 5.3 Raise or replace overly loose similarity thresholds where they allow incomplete resolutions to pass.
- [x] 5.4 Add tests for at least one strengthened merge, rebase, or cherry-pick fixture.

## 6. Harder Coverage for Saturated Suites

- [x] 6.1 Compare recent stored results to identify suites with saturated or near-saturated pass rates.
- [x] 6.2 Add harder domain-relevant fixture variants or stronger assertions for saturated suites where appropriate.
- [x] 6.3 Ensure added fixtures include `purpose`, `difficulty`, and `tags` metadata.
- [x] 6.4 Confirm fixture IDs remain unique and suite fixture loading still passes.

## 7. Documentation

- [x] 7.1 Update `README.md` scoring documentation with `command_equivalence` and `accepted` examples.
- [x] 7.2 Update `CONTRIBUTING.md` fixture authoring guidance for command equivalence, strict selection scoring, state assertions, and similarity scoring.
- [x] 7.3 Document that valid accepted alternatives must be semantically equivalent, not merely similar.

## 8. Verification

- [x] 8.1 Run scorer and benchmark tests covering the changed behavior.
- [x] 8.2 Run the full Python test suite.
- [x] 8.3 Run a mock benchmark pass to verify all fixtures load and score.
- [x] 8.4 Run `openspec validate --change harden-fixture-scoring-and-calibration` and fix any artifact issues.
