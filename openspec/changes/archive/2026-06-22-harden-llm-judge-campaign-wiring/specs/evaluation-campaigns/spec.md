## MODIFIED Requirements

### Requirement: Campaign configuration is immutable and identifiable

Each campaign SHALL have a unique ID and SHALL persist its selected fixtures, models, reasoning efforts, output modes, trial count, scheduler seed, request configuration, scorer configuration, judge configuration and decision-complete judge configuration hash, fixture-generation version, and result schema version.

#### Scenario: Resume with changed configuration

- **WHEN** resume is requested with configuration that differs from the persisted campaign configuration, including judge identity
- **THEN** the runner SHALL reject the resume
- **AND** it SHALL identify the incompatible configuration fields

#### Scenario: Resume legacy judge campaign without judge identity

- **WHEN** a judge-enabled campaign manifest does not contain a decision-complete judge configuration hash
- **THEN** the runner SHALL reject automatic resume with an actionable compatibility error
- **AND** it SHALL NOT reuse unverifiable cached judge decisions

#### Scenario: Resume non-judge campaign

- **WHEN** a campaign contains no `llm_judge` fixtures
- **THEN** the absence of judge configuration identity SHALL not by itself prevent resume
