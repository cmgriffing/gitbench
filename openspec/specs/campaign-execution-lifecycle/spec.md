# campaign-execution-lifecycle Specification

## Purpose
TBD - created by archiving change fix-campaign-execution-lifecycle. Update Purpose after archive.
## Requirements
### Requirement: Campaign runs execute every planned identity
When `gitbench run` is invoked with a campaign ID, the runner SHALL execute the campaign schedule rather than the legacy one-shot model/benchmark loop. Each selected fixture SHALL run once for every selected model, reasoning effort, output mode, and numbered trial.

#### Scenario: Two-trial campaign executes twice
- **WHEN** a user runs one benchmark with 12 fixtures, one model, one output mode, and `--trials 2`
- **THEN** the campaign SHALL execute 24 target attempts
- **AND** the persisted campaign SHALL contain two trial records
- **AND** each trial SHALL contain 12 completed attempt identities

#### Scenario: Both output modes remain separate
- **WHEN** a campaign runs with `--output-mode both`
- **THEN** each trial SHALL execute text and JSON-schema identities separately
- **AND** text and JSON-schema attempts SHALL have distinct raw-attempt identities

### Requirement: Campaign schedules are restart-safe
The campaign store SHALL persist the complete planned schedule or a versioned schedule artifact that can reconstruct the exact planned identities after process restart. Resume SHALL NOT depend on private in-memory attributes.

#### Scenario: Resume after manifest reload
- **WHEN** a planned campaign manifest is written and then loaded in a new process
- **THEN** the resume planner SHALL recover every planned attempt identity
- **AND** missing attempts SHALL be scheduled even when no private runtime schedule object exists

#### Scenario: Scheduler version mismatch
- **WHEN** a persisted campaign schedule was produced by an incompatible scheduler version
- **THEN** resume SHALL reject the campaign with a clear incompatibility error
- **AND** it SHALL NOT silently compute a different attempt order

### Requirement: Campaign resume validates immutable configuration
Before resuming a campaign, the runner SHALL compare the requested benchmark, fixture set, model IDs, reasoning efforts, output modes, trial count, scorer configuration, request configuration, fixture-generation version, and scheduler seed against the persisted campaign configuration.

#### Scenario: Resume with changed trial count
- **WHEN** an existing campaign was planned with three trials and the user resumes with five trials
- **THEN** the runner SHALL reject the resume
- **AND** the error SHALL identify `planned_trial_count` as incompatible

#### Scenario: Resume skips compatible completed attempts
- **WHEN** a campaign contains 95 compatible valid attempts out of 120 planned attempts
- **THEN** resume SHALL schedule only the 25 missing identities
- **AND** it SHALL NOT issue target calls for the 95 completed identities

### Requirement: Raw attempts are persisted before completion counts advance
For each campaign identity, the runner SHALL persist a raw attempt envelope containing identity, status, model output, structured-output state, score, provenance hashes, request telemetry, provider metadata, token usage, cost, timing, retry history, judge evidence, and safety state before marking the attempt complete.

#### Scenario: Completed target call writes raw attempt
- **WHEN** a campaign fixture call returns and scoring completes
- **THEN** a raw attempt envelope SHALL be written for that exact identity
- **AND** the campaign manifest SHALL count it as completed only after the envelope write succeeds

#### Scenario: Provider exhaustion is non-quality
- **WHEN** provider retries are exhausted without a usable response
- **THEN** the raw attempt SHALL be stored as an infrastructure failure
- **AND** it SHALL be excluded from quality denominators
- **AND** the campaign SHALL remain incomplete

#### Scenario: Structured-output validation failure is quality failure
- **WHEN** a provider response violates the required structured-output schema
- **THEN** the raw attempt SHALL be stored as a valid failed quality attempt
- **AND** it SHALL contribute to the mean-success denominator

### Requirement: Campaign aggregates preserve exact comparison dimensions
Campaign aggregation SHALL preserve campaign, model, reasoning effort, output mode, benchmark, and fixture dimensions for exact summaries. Rollups across any of those dimensions SHALL be explicitly named and SHALL NOT replace exact summaries.

#### Scenario: Same fixture in two output modes
- **WHEN** the same fixture has two text attempts and two JSON-schema attempts
- **THEN** exact fixture aggregates SHALL expose separate text and JSON-schema denominators
- **AND** no headline exact aggregate SHALL report all four attempts as one output-mode result

#### Scenario: Same model in two reasoning efforts
- **WHEN** the same base model is evaluated at `low` and `high` reasoning efforts
- **THEN** model campaign summaries SHALL keep the two reasoning efforts distinct
- **AND** raw-attempt lookup SHALL require enough identity fields to select exactly one attempt

### Requirement: Campaign state reflects persisted attempts
After campaign execution, interruption, resume, or repair, the store SHALL recompute trial summaries, fixture aggregates, resource summaries, completed counts, valid counts, excluded counts, and campaign state from persisted raw attempts.

#### Scenario: Full campaign completes
- **WHEN** every planned identity has a valid quality outcome and no excluded attempts
- **THEN** the campaign state SHALL be `complete`
- **AND** completed attempts SHALL equal planned attempts

#### Scenario: Missing attempt remains incomplete
- **WHEN** at least one planned identity has no persisted attempt
- **THEN** the campaign state SHALL be `incomplete`
- **AND** the missing count SHALL be visible in the manifest or derived summary

