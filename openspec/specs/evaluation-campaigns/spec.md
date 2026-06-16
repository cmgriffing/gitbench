# evaluation-campaigns Specification

## Purpose
TBD - created by archiving change add-repeated-evaluation-campaigns. Update Purpose after archive.
## Requirements
### Requirement: Campaigns schedule complete repeated trial rounds

The runner SHALL represent repeated evaluation as a campaign with an immutable configuration and SHALL schedule each selected fixture exactly once per model, reasoning effort, output mode, and trial round.

#### Scenario: Run a three-trial campaign

- **WHEN** a user starts a campaign with three trials, two models, two output modes, and ten fixtures
- **THEN** the campaign SHALL plan 120 target attempts
- **AND** each numbered trial SHALL contain all 40 model/output-mode/fixture combinations

#### Scenario: Run a one-trial smoke campaign

- **WHEN** a user explicitly selects one trial
- **THEN** the runner SHALL create a valid one-trial campaign
- **AND** the campaign SHALL use the same manifest, provenance, and aggregation model as a repeated campaign

### Requirement: Campaign configuration is immutable and identifiable

Each campaign SHALL have a unique ID and SHALL persist its selected fixtures, models, reasoning efforts, output modes, trial count, scheduler seed, request configuration, scorer configuration, fixture-generation version, and result schema version.

#### Scenario: Resume with changed configuration

- **WHEN** resume is requested with configuration that differs from the persisted campaign configuration
- **THEN** the runner SHALL reject the resume
- **AND** it SHALL identify the incompatible configuration fields

### Requirement: Fixture inputs are reproducible across trials

Fixture setup SHALL stabilize Git identities and relevant environment inputs, and every attempt SHALL record hashes for the fixture input, rendered prompt, expected or scoring input, request configuration, and scorer configuration.

#### Scenario: Identical fixture is generated in separate trials

- **WHEN** the same fixture-generation version and campaign seed are used for two trials
- **THEN** the fixture input and rendered prompt hashes SHALL match

#### Scenario: Fixture identity changes unexpectedly

- **WHEN** an existing or newly generated attempt has hashes that differ from the campaign manifest
- **THEN** that attempt SHALL be marked invalid
- **AND** it SHALL not contribute to quality aggregates
- **AND** the campaign SHALL remain incomplete until the mismatch is repaired or the campaign is replaced

### Requirement: Raw attempts are preserved under exact identities

The result store SHALL preserve one raw attempt for every campaign, trial, model, reasoning effort, output mode, and fixture combination and SHALL prevent duplicate valid attempts for the same identity.

#### Scenario: Persist a completed attempt

- **WHEN** a target call and scoring complete
- **THEN** the result store SHALL persist the raw output, score, validation state, provenance, resource usage, and attempt identity before marking the attempt complete

#### Scenario: Duplicate attempt is encountered

- **WHEN** an attempt already exists with the same exact identity and compatible hashes
- **THEN** ordinary execution SHALL reuse the existing attempt
- **AND** it SHALL not issue another target call

### Requirement: Campaigns resume missing work exactly

Interrupted campaigns SHALL resume by scheduling only missing, invalidated, or explicitly repairable attempt identities.

#### Scenario: Resume a partially completed trial

- **WHEN** a campaign contains 95 valid attempts out of 120 planned attempts
- **THEN** resume SHALL schedule the 25 missing attempts
- **AND** it SHALL preserve the 95 valid attempts

#### Scenario: Repair an exhausted transient failure

- **WHEN** a user requests repair for an exact campaign attempt whose provider retries were exhausted
- **THEN** the runner SHALL retry that identity
- **AND** the manifest SHALL retain the prior failure history for auditability

### Requirement: Campaign reliability metrics use explicit denominators

Campaign aggregation SHALL expose `mean_success_rate`, `pass_any_at_n`, planned trials, completed trials, valid attempts, passing attempts, and excluded failure counts without using `pass_at_k` as an ambiguous alias.

#### Scenario: Aggregate a complete fixture

- **WHEN** a fixture passes four of five valid attempts
- **THEN** its mean success rate SHALL be `0.8`
- **AND** its reliability classification SHALL be `flaky`
- **AND** `pass_any_at_5` SHALL be true

#### Scenario: Classify stable fixture outcomes

- **WHEN** every valid attempt for a fixture passes
- **THEN** the fixture SHALL be classified `stable_pass`
- **WHEN** every valid attempt fails
- **THEN** the fixture SHALL be classified `stable_fail`

### Requirement: Campaign completeness distinguishes quality from operational failures

Structured-output parse and schema-validation failures SHALL count as model-quality failures. Transport failures, exhausted provider failures, invalid fixture hashes, and unavailable judge results SHALL be excluded from quality denominators and SHALL make the campaign incomplete.

#### Scenario: Structured response violates its schema

- **WHEN** the provider returns a response that cannot satisfy the required structured-output schema
- **THEN** the attempt SHALL be a valid failed quality attempt

#### Scenario: Provider never returns a response

- **WHEN** target-provider retries are exhausted without a usable response
- **THEN** the attempt SHALL be recorded as an infrastructure failure
- **AND** it SHALL not be counted as a model-quality failure
- **AND** the campaign SHALL be incomplete

### Requirement: Campaign resource usage is reported per trial and in total

Campaign aggregation SHALL report mean cost, token usage, and API time per complete trial as well as total campaign consumption.

#### Scenario: Compare campaigns with different trial counts

- **WHEN** two compatible campaigns have different numbers of completed trials
- **THEN** ranking metrics SHALL use mean resource usage per complete trial
- **AND** each campaign's total consumption SHALL remain available separately

### Requirement: Campaign scheduling records ordering controls

The runner SHALL record the scheduler seed and SHALL balance model and output-mode ordering across trial rounds to reduce systematic time-order effects.

#### Scenario: Reconstruct scheduled order

- **WHEN** a campaign manifest and scheduler version are available
- **THEN** the planned attempt order SHALL be reproducible

### Requirement: Campaign publication honors result safety state

When result safety review is configured, every raw attempt SHALL reach an allowed reviewed state before the campaign is publishable.

#### Scenario: Safety review remains pending

- **WHEN** a complete quality campaign contains an attempt with pending safety review
- **THEN** the campaign SHALL be marked complete but not publishable
- **AND** public raw-attempt queries SHALL not expose that attempt

