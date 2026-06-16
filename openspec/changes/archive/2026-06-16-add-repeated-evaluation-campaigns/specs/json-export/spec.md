## ADDED Requirements

### Requirement: JSON export represents campaigns and attempts

The JSON export SHALL include campaign metadata, trial summaries, fixture reliability aggregates, explicit metric numerators and denominators, resource summaries, and references or records for raw attempts.

#### Scenario: Export a repeated campaign

- **WHEN** a five-trial campaign is exported
- **THEN** the export SHALL identify all five planned trials and their completion states
- **AND** fixture aggregates SHALL include passing and valid attempt counts
- **AND** raw attempts SHALL retain exact campaign and trial identities

### Requirement: JSON export imports historical results as legacy campaigns

The export pipeline SHALL interpret pre-campaign result artifacts as one-trial legacy campaigns without inventing repeated-trial evidence.

#### Scenario: Import a historical artifact

- **WHEN** an artifact from the previous report schema is loaded
- **THEN** it SHALL produce a one-trial campaign marked `legacy`
- **AND** repeated-trial variability fields SHALL be absent or explicitly unavailable

### Requirement: New exports use unambiguous metric names

New campaign exports SHALL use `mean_success_rate` and explicitly named `pass_any_at_n` fields and SHALL NOT use `pass_at_k` to represent ordinary pass rate.

#### Scenario: Read campaign summary metrics

- **WHEN** a consumer reads a campaign model summary
- **THEN** it SHALL be able to distinguish one-attempt mean success from passing at least once in multiple attempts

