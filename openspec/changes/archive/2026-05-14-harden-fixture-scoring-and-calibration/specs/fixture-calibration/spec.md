## ADDED Requirements

### Requirement: Known brittle fixtures are corrected
Fixtures with known incorrect or brittle expectations SHALL be corrected so valid answers pass and objectively wrong expectations are removed.

#### Scenario: Submodule list accepts status form
- **WHEN** the submodule listing fixture asks for the command to list configured submodules
- **THEN** both `git submodule` and `git submodule status` are accepted as correct

#### Scenario: Full hash fixture expects a hash
- **WHEN** the `git_show/f008` fixture asks for the full SHA hash of the commit with message `Second commit`
- **THEN** the fixture no longer expects the literal text `Second commit`

### Requirement: Fixture audit covers every suite
The calibration work SHALL audit every benchmark suite for brittle exact matches, loose similarity thresholds, incorrect expected values, and difficulty labels that do not match fixture complexity.

#### Scenario: All suites are included in audit
- **WHEN** calibration tasks are complete
- **THEN** each of the 17 benchmark suites has been reviewed for scoring robustness and difficulty calibration

#### Scenario: Audit findings are acted on
- **WHEN** a fixture is found to reject valid equivalent answers
- **THEN** the fixture is migrated to a more appropriate scorer or corrected accepted alternatives

#### Scenario: Incorrect expectation is fixed
- **WHEN** a fixture expected value conflicts with the prompt's requested answer
- **THEN** the expected value or scoring method is corrected

### Requirement: Overly permissive conflict scoring is strengthened
Conflict-resolution fixtures SHALL avoid passing incomplete resolutions solely because a returned string is similar to one expected file.

#### Scenario: Multi-file conflict fixture validates relevant files
- **WHEN** a conflict fixture describes required resolutions across multiple files
- **THEN** scoring validates the required resolved content for each relevant file or explicitly scopes the fixture to one file

#### Scenario: Loose similarity threshold is replaced or justified
- **WHEN** a conflict fixture uses broad text similarity scoring
- **THEN** the fixture is either migrated to structured/file-aware scoring or documented as intentionally similarity-based

### Requirement: Saturated suites receive harder coverage
Suites with saturated or near-saturated stored pass rates SHALL be reviewed for harder variants or stronger assertions that test deeper Git reasoning.

#### Scenario: Saturated suite is strengthened
- **WHEN** a suite has recent stored results showing all or nearly all fixtures passing across multiple profiles
- **THEN** the suite gains harder fixture coverage or stricter scoring where appropriate

#### Scenario: Harder fixture remains domain-relevant
- **WHEN** a harder fixture is added
- **THEN** it tests the same benchmark capability rather than introducing unrelated Git behavior

### Requirement: Fixture authoring guidance is updated
Project documentation SHALL explain when to use command equivalence, state assertions, strict selection scoring, and similarity scoring.

#### Scenario: Command fixture guidance exists
- **WHEN** a contributor writes a fixture that asks for a Git command
- **THEN** documentation explains when to use `command_equivalence` and how to declare accepted alternatives

#### Scenario: Selection fixture guidance exists
- **WHEN** a contributor writes a fixture that asks for branches, commits, files, or stash refs to select
- **THEN** documentation explains that extra incorrect selections should fail unless partial credit is explicitly intended
