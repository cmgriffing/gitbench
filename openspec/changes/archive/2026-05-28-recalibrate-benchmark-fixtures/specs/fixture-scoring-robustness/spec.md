## ADDED Requirements

### Requirement: Unordered line-set scoring
The scoring system SHALL support an order-insensitive line-set scoring type for fixtures where the correct answer is a set of lines and order is not part of the skill under test.

#### Scenario: Same lines in different order pass
- **WHEN** a fixture expects lines `A` and `B` using unordered line-set scoring
- **THEN** model output containing `B` then `A` passes

#### Scenario: Missing line fails
- **WHEN** a fixture expects lines `A` and `B` using unordered line-set scoring
- **THEN** model output containing only `A` fails

#### Scenario: Extra line fails
- **WHEN** a fixture expects lines `A` and `B` using unordered line-set scoring
- **THEN** model output containing `A`, `B`, and `C` fails unless the fixture explicitly allows extra lines

### Requirement: Numeric exact scoring
The scoring system SHALL support numeric exact scoring for integer/count answers so formatting noise does not cause false failures while incorrect numbers still fail.

#### Scenario: Whitespace around number passes
- **WHEN** a fixture expects numeric answer `7`
- **THEN** model output `  7  ` passes

#### Scenario: Prose containing only one answer number passes
- **WHEN** a fixture expects numeric answer `7`
- **THEN** model output `The answer is 7.` passes if numeric prose normalization is enabled for that fixture

#### Scenario: Different number fails
- **WHEN** a fixture expects numeric answer `7`
- **THEN** model output `6` fails

### Requirement: Dynamic commit-hash scoring
The scoring system SHALL support commit-hash scoring that derives the expected hash from repository state using a stable fixture-declared selector such as commit subject.

#### Scenario: Short hash by subject passes
- **WHEN** a fixture asks for the short hash of the commit with subject `Fix null pointer bug`
- **THEN** scoring derives that commit hash from the fixture repository and passes the matching short hash

#### Scenario: Commit message fails for hash answer
- **WHEN** a fixture asks for a commit hash
- **THEN** model output containing only the commit message fails

#### Scenario: Wrong hash fails
- **WHEN** a fixture asks for the short hash of a selected commit
- **THEN** a short hash for a different commit fails

### Requirement: Semantic structured-value scoring
The scoring system SHALL support semantic scoring for structured values where textual formatting is not the core skill, such as JSON conflict-resolution outputs.

#### Scenario: Equivalent JSON formatting passes
- **WHEN** a fixture expects a JSON object
- **THEN** model output with the same parsed JSON value passes even if whitespace or property order differs

#### Scenario: Invalid JSON fails
- **WHEN** a fixture expects valid JSON
- **THEN** model output that cannot be parsed as JSON fails

#### Scenario: Different JSON value fails
- **WHEN** a fixture expects a JSON object with `version` equal to `2.0.0`
- **THEN** model output with `version` equal to `1.0.0` fails

### Requirement: Conflict-resolution prompts declare policy
Conflict-resolution fixtures SHALL state the intended resolution policy clearly enough that deterministic scoring evaluates the target skill rather than an unstated preference.

#### Scenario: Current-side resolution is explicit
- **WHEN** a conflict fixture expects the current branch value to win
- **THEN** the prompt identifies that policy rather than relying on ambiguous branch labels

#### Scenario: Combined resolution is explicit
- **WHEN** a conflict fixture expects preserving changes from both sides
- **THEN** the prompt describes that combined-resolution policy and scoring validates the combined output
