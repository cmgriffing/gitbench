# llm-judge-scoring Specification

## Purpose
TBD - created by archiving change add-llm-judge. Update Purpose after archive.
## Requirements
### Requirement: Judge configuration in gitbench.json
The system SHALL require a top-level `judge` section in `gitbench.json` for benchmarks whose fixtures declare `scoring.type: llm_judge`. Running a judge-required benchmark without judge configuration SHALL exit with an error (unless all models are mock).

The `judge` section MUST have:
- `profile`: Name of a model profile defined in `models` to use as the judge model group. Every model in the profile is called for ensemble averaging.

#### Scenario: Judge section present
- **WHEN** `gitbench.json` contains `"judge": {"profile": "openrouter-llms-as-judges"}`
- **THEN** the system SHALL use the judge for all benchmarks containing `llm_judge` fixtures

#### Scenario: Judge section absent for judge-required benchmark
- **WHEN** `gitbench.json` has no `judge` key and a benchmark with `llm_judge` fixtures (e.g. `commit_messages`) is run
- **THEN** the system SHALL exit with an error indicating that a judge profile is required

#### Scenario: Judge section absent for non-judge benchmark
- **WHEN** `gitbench.json` has no `judge` key and a benchmark that has no `llm_judge` fixtures is run (e.g. `git_bisect`)
- **THEN** the system SHALL run normally without a judge

#### Scenario: Judge profile not found
- **WHEN** the `judge.profile` references a profile not defined in `models`
- **THEN** the system SHALL exit with an error indicating the profile is not found

### Requirement: JudgeClient evaluates commit messages via ensemble averaging
The system SHALL provide a `JudgeClient` class that wraps multiple model clients and returns the **average** of their scores.

`JudgeClient` MUST:
- Accept a list of ``ModelInterface`` instances at initialization
- Call **every** model for each evaluation
- Average the successful scores; exclude failed models from the average
- Provide an `evaluate_commit_message(diff, message)` method that returns a `float` between 0.0 and 1.0
- Construct a prompt that includes the diff and message, asking the model to rate quality
- Parse each model response to extract a numeric rating

#### Scenario: Perfect commit message
- **WHEN** the diff shows adding a file `hello.txt` and the message is "Add hello.txt with greeting message"
- **THEN** the judge SHALL return a score ≥ 0.7

#### Scenario: Wrong commit message
- **WHEN** the diff shows adding a file `hello.txt` and the message is "Fix login bug"
- **THEN** the judge SHALL return a score < 0.5

#### Scenario: Vague commit message
- **WHEN** the diff shows adding three new files `config.py`, `main.py`, `utils.py` and the message is "Update files"
- **THEN** the judge SHALL return a score between 0.3 and 0.6

#### Scenario: Non-numeric judge response
- **WHEN** the judge model returns a response that cannot be parsed as a number
- **THEN** `evaluate_commit_message` SHALL raise a `ValueError`

### Requirement: Judge gating is declared per fixture
The system SHALL invoke the LLM judge if and only if a fixture declares `scoring.type: llm_judge`. No benchmark-level allowlist or diff-presence heuristic SHALL participate in judge routing.

The `Scorer` class SHALL accept an optional `JudgeClient` and dispatch to it for `llm_judge` fixtures.

#### Scenario: llm_judge fixture routed to judge
- **WHEN** a fixture with `scoring.type: llm_judge` is scored and a judge is configured
- **THEN** the score comes from `JudgeClient` ensemble averaging, with `passed = similarity >= threshold`

#### Scenario: similarity fixture never routed to judge
- **WHEN** a fixture with `scoring.type: similarity` is scored, even with a judge configured and a diff available
- **THEN** the score comes from SequenceMatcher only

#### Scenario: llm_judge without judge client
- **WHEN** a fixture with `scoring.type: llm_judge` is scored and no judge client is configured
- **THEN** the result is a failed score with an error indicating a judge is required (normally prevented by CLI preflight)

### Requirement: Judge-required benchmarks are discovered from fixtures
The system SHALL determine which benchmarks require a judge by scanning their fixtures for `scoring.type: llm_judge`, replacing the hardcoded `JUDGE_REQUIRED_BENCHMARKS` constant.

#### Scenario: Preflight error without judge profile
- **WHEN** a requested benchmark contains llm_judge fixtures, no `judge` section exists in `gitbench.json`, and models are not all mock
- **THEN** the CLI exits with the existing "requires an LLM judge" error before any fixtures run

#### Scenario: Mock-models exemption preserved
- **WHEN** all requested models are mock variants
- **THEN** llm_judge benchmarks run without a judge profile, as today

#### Scenario: No stale allowlist
- **WHEN** a new benchmark's fixtures declare `scoring.type: llm_judge`
- **THEN** preflight validation and judge wiring apply to it without any code or config change

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

### Requirement: Runner wires judge into benchmark execution
The `BenchmarkRunner` SHALL construct a single judge-aware `Scorer` when a judge is configured. Fixtures declaring `scoring.type: llm_judge` SHALL be evaluated by that scorer with the rendered diff, original prompt, and campaign scoring context. Non-judge fixtures SHALL retain benchmark-specific evaluation behavior and SHALL NOT invoke the judge.

#### Scenario: Runner with judge configuration
- **WHEN** the runner is initialized with a valid `judge` section and evaluates an `llm_judge` fixture
- **THEN** the runner's judge-aware `Scorer` SHALL receive the fixture, target output, rendered diff, original prompt, and campaign scoring context

#### Scenario: Non-judge benchmark with judge configuration
- **WHEN** the runner has a judge configured but evaluates a fixture with a benchmark-specific non-judge scoring type
- **THEN** the benchmark-specific scoring hook SHALL evaluate the fixture
- **AND** the judge SHALL NOT be called

#### Scenario: Runner without judge configuration
- **WHEN** the runner is initialized without a `judge` section
- **THEN** non-judge fixtures SHALL run through their benchmark-specific evaluation normally
- **AND** only `llm_judge` fixtures would error, normally prevented by preflight

#### Scenario: Campaign judge exhaustion remains unscored
- **WHEN** all judge models fail while the corrected runner dispatches a campaign `llm_judge` fixture
- **THEN** the attempt SHALL remain unscored with judge evidence
- **AND** it SHALL NOT be converted into a benchmark-specific or heuristic quality score

### Requirement: Judge failure handling preserves scoring consistency

LLM-judge scoring SHALL retry according to configured policy and SHALL mark the target attempt unscored if required judge results remain unavailable. It SHALL NOT fall back to a different scoring method within the campaign.

#### Scenario: A required judge remains unavailable

- **WHEN** judge retries are exhausted and the configured aggregate cannot be produced
- **THEN** the target attempt SHALL be marked unscored
- **AND** the campaign SHALL remain incomplete
- **AND** no heuristic fallback score SHALL enter campaign quality aggregates

### Requirement: Judge decisions are cached by campaign evidence identity

LLM-judge decisions SHALL be cached by fixture input hash, target output hash, and judge configuration hash within a campaign.

#### Scenario: Identical output is judged again

- **WHEN** the same fixture input, target output, and judge configuration recur in the campaign
- **THEN** the scorer SHALL reuse the cached judge decision
- **AND** it SHALL not issue duplicate judge calls

#### Scenario: Judge configuration changes

- **WHEN** any judge model, prompt, aggregation rule, or request configuration changes
- **THEN** the prior cached decision SHALL not be reused

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

### Requirement: Campaign judge scoring uses cache keys
Campaign scoring SHALL pass a cache key to judge evaluation derived from the fixture input hash, target output hash, and judge configuration hash. Repeated identical target outputs for the same fixture input within a campaign SHALL reuse cached judge evidence or score.

#### Scenario: Identical output judged once
- **WHEN** two attempts in the same campaign have the same fixture input hash, target output hash, and judge configuration hash
- **THEN** the second attempt SHALL use the campaign judge cache
- **AND** it SHALL NOT issue duplicate judge model calls

#### Scenario: Different judge configuration bypasses cache
- **WHEN** the judge configuration hash changes
- **THEN** an otherwise identical fixture input and target output SHALL be judged again

