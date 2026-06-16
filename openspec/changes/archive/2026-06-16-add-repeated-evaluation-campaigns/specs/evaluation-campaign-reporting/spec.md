## ADDED Requirements

### Requirement: Reports select a campaign globally

The report application SHALL provide a campaign selector shared across campaign-sensitive pages and SHALL default to the latest completed publishable campaign.

#### Scenario: Select another campaign

- **WHEN** a user selects a campaign from any report page
- **THEN** campaign-sensitive summaries, charts, tables, and links SHALL use that campaign
- **AND** navigation SHALL preserve the selected campaign

#### Scenario: No completed campaign exists

- **WHEN** the report contains only incomplete campaigns
- **THEN** the latest incomplete campaign SHALL be selected
- **AND** the interface SHALL prominently identify it as incomplete

### Requirement: Campaign status and comparability are visible

The report SHALL display campaign trial counts, completeness, publication state, legacy state, and configuration compatibility wherever campaign data is selected or compared.

#### Scenario: View a legacy campaign

- **WHEN** a historical one-result artifact is imported
- **THEN** the UI SHALL label it as a one-trial legacy campaign
- **AND** it SHALL not imply that stability was measured

#### Scenario: Compare incompatible campaigns

- **WHEN** campaigns differ in fixture inputs, suite membership, scoring configuration, or request configuration
- **THEN** the UI SHALL identify the incompatibility
- **AND** it SHALL not compute a default reliability delta

### Requirement: Aggregate reliability is traceable to raw attempts

Model, benchmark, and fixture summaries SHALL expose explicit pass counts and denominators and SHALL link to the raw attempts that produced the aggregate.

#### Scenario: Inspect a flaky fixture

- **WHEN** a fixture summary reports four passes in five attempts
- **THEN** the user SHALL be able to expand or navigate to all five attempts
- **AND** each attempt SHALL show its quality result, output mode, score, validation state, trial, resource usage, and available provenance

### Requirement: Report rankings use complete balanced campaigns

Default leaderboards and cross-model comparisons SHALL include only complete balanced campaign summaries.

#### Scenario: Campaign is partially complete

- **WHEN** one model has fewer valid scheduled attempts than another
- **THEN** the incomplete model SHALL not appear in the default ranking
- **AND** the user MAY explicitly reveal it with its missing counts visible

### Requirement: UI reliability states are accessible

Campaign and fixture reliability states SHALL be communicated with text or counts in addition to color and SHALL be operable with keyboard and assistive technologies.

#### Scenario: Reliability heatmap is read without color

- **WHEN** a user reads a heatmap cell with assistive technology
- **THEN** the cell SHALL announce the model or fixture, passing attempts, total valid attempts, and reliability classification

### Requirement: History treats campaigns as the comparison unit

History views SHALL show one primary point or row per campaign and SHALL provide trial-level detail without presenting trials as independent benchmark releases.

#### Scenario: Expand a history row

- **WHEN** a user expands a campaign in history
- **THEN** the report SHALL show trial summaries and completion details
- **AND** campaign-level changes SHALL remain the primary history comparison

