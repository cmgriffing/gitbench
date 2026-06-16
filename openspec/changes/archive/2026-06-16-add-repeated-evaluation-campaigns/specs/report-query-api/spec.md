## ADDED Requirements

### Requirement: Report storage persists campaign entities

The report database SHALL persist campaigns, trials, raw fixture attempts, fixture aggregates, model and benchmark campaign summaries, resource summaries, judge evidence, and publication state with referential integrity.

#### Scenario: Build a report database

- **WHEN** campaign result artifacts are ingested
- **THEN** each raw attempt SHALL be associated with exactly one campaign and trial
- **AND** aggregate rows SHALL retain their source campaign identity

### Requirement: Campaign-sensitive queries accept an explicit selector

Report-store methods and HTTP endpoints that return benchmark results SHALL accept a campaign selector and SHALL include the selected campaign's status in the response.

#### Scenario: Query a model in a selected campaign

- **WHEN** a client requests model results with a campaign ID
- **THEN** only results and aggregates from that campaign SHALL be returned

#### Scenario: Omit campaign selection

- **WHEN** a client omits the campaign selector
- **THEN** the API SHALL select the latest completed publishable campaign
- **AND** it SHALL return the resolved campaign ID

### Requirement: Raw attempt queries are bounded

The API SHALL expose raw attempts through exact-identity or paginated queries and SHALL not embed all raw outputs in aggregate responses.

#### Scenario: List attempts for a fixture aggregate

- **WHEN** a client requests attempts for one fixture, model, effort, and output mode
- **THEN** the API SHALL return a bounded page with trial identities and attempt evidence

### Requirement: Public queries enforce publication safety

Public report queries SHALL exclude raw attempts that have not reached an allowed safety state when campaign safety review is required.

#### Scenario: Query an unpublished attempt

- **WHEN** a public client requests an attempt whose safety state is pending or blocked
- **THEN** the API SHALL not return its raw prompt or output content

