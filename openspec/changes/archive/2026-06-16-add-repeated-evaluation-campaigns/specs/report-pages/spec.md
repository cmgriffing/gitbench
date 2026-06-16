## ADDED Requirements

### Requirement: Report pages preserve campaign selection

Overview, model, benchmark, fixture, compare, history, model-index, and directory report pages SHALL resolve campaign-sensitive data from the shared selected campaign.

#### Scenario: Navigate from overview to a fixture

- **WHEN** a user selects a campaign and follows a link from overview to a fixture page
- **THEN** the fixture page SHALL show data from the same campaign

### Requirement: Overview reports campaign reliability

The overview SHALL present mean one-attempt success, valid attempt counts, planned and completed trials, and campaign completeness for each ranked model configuration.

#### Scenario: View an overview model row

- **WHEN** a complete five-trial campaign is selected
- **THEN** the row SHALL display its mean success rate and five completed trials
- **AND** trial variability SHALL be available without changing the meaning of reasoning-effort range visuals

### Requirement: Model detail reports stability classifications

Model detail pages SHALL report stable-pass, flaky, and stable-fail fixture counts by benchmark and output mode and SHALL provide access to underlying attempts.

#### Scenario: Inspect model flakiness

- **WHEN** a model has fixtures with mixed outcomes across trials
- **THEN** the model page SHALL identify those fixtures as flaky
- **AND** it SHALL show pass counts and denominators

### Requirement: Benchmark and fixture pages aggregate repeated attempts

Benchmark pages SHALL display per-fixture reliability aggregates, and fixture pages SHALL display per-model and output-mode attempt aggregates with expandable raw evidence.

#### Scenario: View a benchmark cell

- **WHEN** a model passes a fixture four times in five valid attempts
- **THEN** the benchmark cell SHALL display `4/5` or equivalent explicit text
- **AND** it SHALL be identified as flaky

#### Scenario: Expand fixture attempts

- **WHEN** a user expands an aggregate on a fixture page
- **THEN** each trial SHALL show output, score, validation state, provider provenance, judge evidence, cost, tokens, and API time when available

### Requirement: Compare pages use reliability deltas

Compare pages SHALL compare fixture pass probabilities and attempt counts rather than treating a repeated campaign as one binary gained, lost, or agreed outcome.

#### Scenario: Compare output modes

- **WHEN** structured output passes four of five attempts and text passes two of five for the same fixture
- **THEN** the comparison SHALL classify structured output as more reliable
- **AND** it SHALL display both attempt ratios

### Requirement: History groups trials under campaigns

The history page SHALL use campaigns as primary rows or points and SHALL expose trials as nested detail.

#### Scenario: Calculate a historical delta

- **WHEN** two campaigns have compatible inputs and configuration
- **THEN** history MAY calculate the change in mean success rate
- **WHEN** they are incompatible
- **THEN** history SHALL withhold the delta and explain why

