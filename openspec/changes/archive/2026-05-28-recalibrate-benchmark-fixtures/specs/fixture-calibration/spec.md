## ADDED Requirements

### Requirement: Current zero-pass fixture defects are corrected
Fixtures with current stored zero-pass results that are caused by incorrect expectations, order-sensitive valid answers, or setup mismatches SHALL be corrected before they are treated as hard benchmark coverage.

#### Scenario: Order-insensitive log message lists pass
- **WHEN** a git-log fixture asks for all matching commit messages without requiring chronological or reverse-chronological order
- **THEN** the fixture accepts the correct set of messages in either order and rejects missing or extra messages

#### Scenario: Dynamic short hash fixture derives expected value
- **WHEN** a git-log fixture asks for the short hash of the commit with a known subject
- **THEN** scoring derives the expected hash from the fixture repository instead of comparing against a static commit message

#### Scenario: Merge-count setup creates merge commits
- **WHEN** a fixture expects `git log --merges` to count merge commits
- **THEN** the fixture setup creates non-fast-forward merge commits or the expected count is corrected to match the actual repository

### Requirement: Low-pass fixture audit is data-driven
Fixture calibration SHALL prioritize stored zero-pass and low-pass fixtures using current result data, grouped by benchmark, fixture, scoring type, and representative model outputs.

#### Scenario: Low-pass fixtures are ranked before audit
- **WHEN** calibration work begins
- **THEN** fixtures are ranked by observed pass rate and the audit starts with zero-pass fixtures followed by low-pass fixtures

#### Scenario: Suspicious exact-match counts are verified
- **WHEN** an exact-match counting fixture has very low pass rate and most failed outputs agree on a different number
- **THEN** the expected value is verified against the actual command output before changing prompts or difficulty

#### Scenario: Fixture bugs are separated from model weakness
- **WHEN** a low-pass fixture is reviewed
- **THEN** the audit records whether the primary issue is fixture setup, expected value, scoring brittleness, prompt ambiguity, or genuine task difficulty

### Requirement: Fixture self-checks validate expected answers
The calibration workflow SHALL include automated fixture self-checks that execute fixture setup and verify expected answers against generated repository state where the expected value is objectively derivable.

#### Scenario: Static expected hash is flagged
- **WHEN** a fixture asks for a commit hash but stores a non-hash expected value
- **THEN** the self-check flags the fixture before a benchmark run is accepted

#### Scenario: Multi-line exact match is flagged for order review
- **WHEN** a fixture uses exact match with multiple output lines
- **THEN** the self-check flags it unless the fixture explicitly documents that order is part of the requirement

#### Scenario: Git command-derived expected answer is checked
- **WHEN** a fixture has an expected answer that can be derived by running a Git command against the setup repository
- **THEN** the self-check compares the fixture expectation to the derived value and reports mismatches

### Requirement: Difficulty labels are recalibrated after corrections
Difficulty labels SHALL be reviewed after fixture and scoring corrections using observed pass rates and manual domain judgment.

#### Scenario: Difficulty review happens after defect fixes
- **WHEN** zero-pass and low-pass fixture defects have been corrected
- **THEN** difficulty labels are recalibrated from corrected fixture behavior rather than from known-broken historical results

#### Scenario: Observed pass-rate bands inform labels
- **WHEN** a fixture has enough stored results after correction
- **THEN** the difficulty review uses observed pass-rate bands as input while allowing documented manual overrides

#### Scenario: Suite version changes for comparability
- **WHEN** fixture expectations, prompts, or scoring rules are changed in a way that affects pass/fail outcomes
- **THEN** the benchmark suite version is bumped so new results are not treated as directly comparable to old results
