## MODIFIED Requirements

### Requirement: Judge failure handling
The system SHALL call **every** model in the judge profile and average their scores.

Each model adapter is configured with 5 retries:
- The adapter SHALL retry with exponential backoff on transient failures
- On rate limits (HTTP 429), the adapter SHALL respect the ``Retry-After`` header
- Failed models are excluded from the average; only successful scores count
- In legacy one-shot scoring, if all models in the profile fail, the system SHALL fall back to ``SequenceMatcher`` and the resulting ``Score`` SHALL have a non-null ``error`` field containing "judge_failed"
- In campaign scoring, if all models in the profile fail, the attempt SHALL be marked unscored with judge evidence, SHALL be excluded from quality denominators, and SHALL make the campaign incomplete
- Fallback behavior lives in the `llm_judge` scoring branch, not the `similarity` branch.

#### Scenario: Judge averages multiple model scores
- **WHEN** the judge profile has 3 models returning 0.8, 0.6, and 0.7
- **THEN** the judge SHALL return 0.7 (the average)

#### Scenario: Judge excludes failed model from average
- **WHEN** one model fails and two return 0.8 and 0.4
- **THEN** the judge SHALL return 0.6 (average of the two successful scores)

#### Scenario: All judge models fail in legacy one-shot scoring
- **WHEN** every model in the judge profile exhausts its retries while scoring an llm_judge fixture outside campaign execution
- **THEN** the score falls back to SequenceMatcher against `fixture.expected`
- **AND** `Score.error` contains "judge_failed"

#### Scenario: All judge models fail in campaign scoring
- **WHEN** every model in the judge profile exhausts its retries while scoring an llm_judge fixture inside campaign execution
- **THEN** the campaign attempt SHALL be unscored
- **AND** judge evidence SHALL preserve the failed member results
- **AND** the attempt SHALL not count as a model-quality failure

#### Scenario: Partial judge failure
- **WHEN** one judge model fails and others return scores
- **THEN** the average of successful scores is used and no error is set

## ADDED Requirements

### Requirement: Campaign judge scoring uses cache keys
Campaign scoring SHALL pass a cache key to judge evaluation derived from the fixture input hash, target output hash, and judge configuration hash. Repeated identical target outputs for the same fixture input within a campaign SHALL reuse cached judge evidence or score.

#### Scenario: Identical output judged once
- **WHEN** two attempts in the same campaign have the same fixture input hash, target output hash, and judge configuration hash
- **THEN** the second attempt SHALL use the campaign judge cache
- **AND** it SHALL NOT issue duplicate judge model calls

#### Scenario: Different judge configuration bypasses cache
- **WHEN** the judge configuration hash changes
- **THEN** an otherwise identical fixture input and target output SHALL be judged again
