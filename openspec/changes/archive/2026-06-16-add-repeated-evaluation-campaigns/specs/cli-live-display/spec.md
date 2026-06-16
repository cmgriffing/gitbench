## ADDED Requirements

### Requirement: CLI displays campaign scope before execution

Before starting a campaign, the CLI SHALL display the selected models, efforts, output modes, fixtures, planned trials, total target attempts, and estimated additional judge and safety calls when calculable.

#### Scenario: Preview an expensive campaign

- **WHEN** a campaign plans multiple trial rounds
- **THEN** the confirmation display SHALL show total planned calls rather than only one-trial counts

### Requirement: CLI displays trial and campaign progress

During execution, the CLI SHALL show the campaign ID, current trial, completed and planned attempts, failure counts, and resume state.

#### Scenario: Resume a campaign

- **WHEN** execution resumes with existing valid attempts
- **THEN** the live display SHALL identify reused attempts and remaining attempts

### Requirement: CLI completion distinguishes status dimensions

At exit, the CLI SHALL separately report quality completion, operational failures, safety/publication state, and aggregate resource consumption.

#### Scenario: Finish with judge failures

- **WHEN** target attempts complete but judge attempts remain unscored
- **THEN** the CLI SHALL report the campaign as incomplete
- **AND** it SHALL not print a final complete ranking

