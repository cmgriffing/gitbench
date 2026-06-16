## ADDED Requirements

### Requirement: Model call failures preserve campaign denominator semantics

Model call retry handling SHALL classify returned invalid structured output as a model-quality failure and SHALL classify exhausted transport, timeout, rate-limit, or provider failures as operational failures that make the campaign incomplete.

#### Scenario: Structured response cannot be parsed

- **WHEN** a target call returns content but the required structured output cannot be parsed or validated
- **THEN** the attempt SHALL count as a failed quality attempt

#### Scenario: Retry policy is exhausted

- **WHEN** no target response is available after configured retries
- **THEN** the attempt SHALL be recorded with retry history and operational failure type
- **AND** it SHALL not enter the quality denominator

### Requirement: Model call provenance supports variance analysis

Each target attempt SHALL record the normalized request configuration, retry history, and available provider routing metadata.

#### Scenario: Provider route metadata is unavailable

- **WHEN** the provider does not expose route information
- **THEN** the attempt SHALL record that provenance as unavailable
- **AND** it SHALL not infer a route from latency or output behavior

