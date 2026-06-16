## ADDED Requirements

### Requirement: CostValueChart ranks comparable per-trial cost and reliability

`CostValueChart` SHALL plot mean cost per complete trial against mean one-attempt success for complete campaign summaries and SHALL expose total campaign cost separately.

#### Scenario: Render a five-trial campaign

- **WHEN** a model campaign summary has five complete trials
- **THEN** its cost axis SHALL use mean cost per complete trial
- **AND** its value axis SHALL use mean one-attempt success
- **AND** the tooltip SHALL show total campaign cost and attempt counts

#### Scenario: Campaign cost is partial

- **WHEN** pricing data is incomplete
- **THEN** the point SHALL be identified as partial
- **AND** it SHALL be excluded from default cost ranking

