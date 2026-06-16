## ADDED Requirements

### Requirement: Runtime tracking retains attempt, trial, and campaign scopes

Runtime tracking SHALL record target API time for each attempt and SHALL aggregate mean API time per complete trial, trial variability, total campaign API time, and wall-clock duration as distinct fields.

#### Scenario: Aggregate parallel execution

- **WHEN** attempts execute concurrently
- **THEN** total target API time SHALL equal the sum of recorded attempt API times
- **AND** campaign wall-clock duration SHALL remain a separate non-additive value

### Requirement: Failed calls retain runtime consumption

Runtime tracking SHALL preserve time spent on retries and exhausted calls and SHALL identify whether that consumption belongs to valid quality attempts or operational failures.

#### Scenario: Provider retries are exhausted

- **WHEN** an attempt fails after multiple provider calls
- **THEN** its consumed API time SHALL remain in campaign operational totals
- **AND** it SHALL not create a valid quality denominator

