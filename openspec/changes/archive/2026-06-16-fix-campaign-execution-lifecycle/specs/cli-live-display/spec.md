## ADDED Requirements

### Requirement: Campaign display reflects actual execution
When a campaign is running, the live display and non-TTY fallback SHALL show actual campaign execution counts derived from the campaign schedule and persisted attempts, not only planned preview counts.

#### Scenario: Trial progress advances
- **WHEN** a two-trial campaign completes one attempt
- **THEN** the display SHALL increment completed campaign attempts by one
- **AND** it SHALL show the current trial or aggregate trial progress

#### Scenario: Reused attempts are visible
- **WHEN** resume skips compatible persisted attempts
- **THEN** the display SHALL show reused attempt counts separately from newly executed attempts
- **AND** remaining attempts SHALL equal planned attempts minus reused and newly completed attempts

### Requirement: Campaign display distinguishes failure classes
Campaign progress output SHALL distinguish quality failures, infrastructure failures, invalid/hash-mismatch attempts, unscored attempts, and safety/publishability state.

#### Scenario: Infrastructure failure during campaign
- **WHEN** a provider attempt exhausts retries during a campaign
- **THEN** the display SHALL count it as an infrastructure failure
- **AND** it SHALL not present it as an ordinary model-quality failed fixture

#### Scenario: Campaign remains unpublished
- **WHEN** a complete campaign has pending or blocked safety review
- **THEN** the final display SHALL show that the campaign is complete but not publishable
