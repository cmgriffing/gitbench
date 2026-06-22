## ADDED Requirements

### Requirement: Evaluation framework failures are non-quality outcomes
Failures in benchmark setup, fixture generation, scoring configuration, or scoring execution that prevent a valid comparison SHALL be recorded as infrastructure failures and excluded from model-quality denominators.

#### Scenario: Benchmark setup signature failure
- **WHEN** a benchmark cannot accept the fixture-generation inputs required by the runner
- **THEN** the attempt SHALL be recorded as an infrastructure failure
- **AND** it SHALL NOT count as a valid model failure

#### Scenario: Unsupported scoring configuration reaches execution
- **WHEN** a fixture scoring type has no valid generic or benchmark-specific evaluation path
- **THEN** the attempt SHALL be recorded as an infrastructure failure with a diagnostic error
- **AND** the campaign SHALL remain incomplete

#### Scenario: Structured model response remains a quality failure
- **WHEN** benchmark setup and scoring are available but the model response violates its structured-output contract
- **THEN** the attempt SHALL remain a valid failed quality attempt
