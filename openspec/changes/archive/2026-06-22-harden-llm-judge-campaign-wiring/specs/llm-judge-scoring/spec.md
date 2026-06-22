## ADDED Requirements

### Requirement: Campaign judge cache has campaign lifetime
The system SHALL create one judge cache per campaign and SHALL reuse it across compatible runners, output modes, trials, process restart, and campaign resume. Cache entries SHALL NOT be shared between different campaign IDs.

#### Scenario: Identical evidence across runners
- **WHEN** two runners in the same campaign produce the same fixture input hash, target output hash, and judge configuration hash
- **THEN** only one judge ensemble evaluation SHALL be issued
- **AND** both attempts SHALL receive the same judge decision

#### Scenario: Resume loads prior judge decision
- **WHEN** a campaign restarts after persisting a judge decision and a later attempt has the same evidence identity
- **THEN** the persisted decision SHALL be reused without duplicate judge calls

#### Scenario: Different campaign does not reuse cache
- **WHEN** another campaign produces otherwise identical judge evidence
- **THEN** it SHALL use that campaign's own cache

### Requirement: Concurrent identical judge requests are single-flight
Concurrent judge requests with the same evidence identity SHALL result in at most one ensemble evaluation. Requests with different evidence identities SHALL remain independently executable.

#### Scenario: Concurrent cache miss for one key
- **WHEN** two workers request the same uncached judge evidence concurrently
- **THEN** one worker SHALL perform the judge calls
- **AND** the other SHALL wait for and reuse the resulting evidence

#### Scenario: Concurrent requests for different keys
- **WHEN** workers request different judge evidence identities
- **THEN** the cache SHALL NOT serialize their judge evaluations solely because they share a campaign

### Requirement: Judge configuration identity covers decision inputs
The judge configuration hash SHALL include the ordered judge model identities, relevant provider and reasoning settings, judge request configuration, judge prompt or rubric version, and aggregation algorithm/version. It MUST exclude credentials and secrets.

#### Scenario: Rubric changes
- **WHEN** the judge prompt or rubric version changes
- **THEN** the judge configuration hash SHALL change
- **AND** prior cache entries SHALL not be reused

#### Scenario: Aggregation changes
- **WHEN** the judge aggregation algorithm or version changes
- **THEN** the judge configuration hash SHALL change

#### Scenario: Secret rotation
- **WHEN** an API credential changes without changing decision-relevant configuration
- **THEN** the credential SHALL not appear in persisted identity data

## MODIFIED Requirements

### Requirement: Judge member evidence is auditable

The result store and campaign judge cache SHALL retain member-level judge scores, aggregation outcome, model/provider provenance, failure state, judge configuration hash, cache identity, and whether the decision was reused. Cache hits SHALL preserve the original member evidence rather than returning only an aggregate score.

#### Scenario: Inspect a directly judged fixture

- **WHEN** a user opens raw evidence for an uncached LLM-judged attempt
- **THEN** each judge member result and the final aggregation SHALL be available subject to publication safety rules
- **AND** the evidence SHALL indicate that the judge ensemble was called

#### Scenario: Inspect a cached judged fixture

- **WHEN** a user opens raw evidence for an attempt that reused a campaign judge decision
- **THEN** the original member results and final aggregation SHALL remain available
- **AND** the evidence SHALL indicate a cache hit and its evidence identity
