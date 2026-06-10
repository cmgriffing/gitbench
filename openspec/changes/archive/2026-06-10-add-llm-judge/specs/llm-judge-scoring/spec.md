## ADDED Requirements

### Requirement: Judge configuration in gitbench.json
The system SHALL require a top-level `judge` section in `gitbench.json` for benchmarks that use LLM judge scoring (currently `commit_messages`). Running a judge-required benchmark without judge configuration SHALL exit with an error.

The `judge` section MUST have:
- `profile`: Name of a model profile defined in `models` to use as the judge model group. The first model in the profile is used for all judge calls.

#### Scenario: Judge section present
- **WHEN** `gitbench.json` contains `"judge": {"profile": "openrouter-llms-as-judges"}`
- **THEN** the system SHALL use the judge for all judge-required benchmarks

#### Scenario: Judge section absent for judge-required benchmark
- **WHEN** `gitbench.json` has no `judge` key and a judge-required benchmark (e.g. `commit_messages`) is run
- **THEN** the system SHALL exit with an error indicating that a judge profile is required

#### Scenario: Judge section absent for non-judge benchmark
- **WHEN** `gitbench.json` has no `judge` key and a benchmark that does not require a judge is run (e.g. `git_bisect`)
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

### Requirement: Scorer integrates judge for similarity-type benchmarks
The `Scorer` class SHALL accept an optional `JudgeClient` and use it for benchmarks configured to use judge scoring.

For judge-enabled benchmarks with `scoring.type: similarity`:
- The scorer SHALL call `JudgeClient.evaluate_commit_message()` instead of `difflib.SequenceMatcher`
- The returned score SHALL be used as the `similarity` field on `Score`
- The `passed` field SHALL be computed as `similarity >= threshold` (unchanged behavior)

#### Scenario: Judge scoring a commit_messages fixture
- **WHEN** scoring a `commit_messages` fixture with a judge configured and the judge returns 0.85
- **THEN** the resulting `Score.similarity` SHALL be 0.85 and `Score.passed` SHALL be `True` if the fixture threshold is ≤ 0.85

#### Scenario: No judge configured for similarity-type benchmark
- **WHEN** scoring a judge-required fixture without a judge configured
- **THEN** this scenario is prevented by the CLI validation — the run exits before scoring begins

#### Scenario: Non-similarity scoring type with judge
- **WHEN** scoring a fixture with `scoring.type` other than `similarity` (e.g., `exact_match`)
- **THEN** the scorer SHALL use the existing scoring logic regardless of judge configuration

### Requirement: Judge failure handling
The system SHALL call **every** model in the judge profile and average their scores.

Each model adapter is configured with 5 retries:
- The adapter SHALL retry with exponential backoff on transient failures
- On rate limits (HTTP 429), the adapter SHALL respect the ``Retry-After`` header
- Failed models are excluded from the average; only successful scores count
- If all models in the profile fail, the system SHALL fall back to ``SequenceMatcher``
- The resulting ``Score`` SHALL have a non-null ``error`` field containing "judge_failed"

#### Scenario: Judge averages multiple model scores
- **WHEN** the judge profile has 3 models returning 0.8, 0.6, and 0.7
- **THEN** the judge SHALL return 0.7 (the average)

#### Scenario: Judge excludes failed model from average
- **WHEN** one model fails and two return 0.8 and 0.4
- **THEN** the judge SHALL return 0.6 (average of the two successful scores)

#### Scenario: All judge models fail
- **WHEN** every model in the judge profile exhausts its retries
- **THEN** the system SHALL fall back to ``SequenceMatcher`` scoring
- **THEN** the ``Score.error`` field SHALL contain "judge_failed"

### Requirement: Runner wires judge into benchmark execution
The `BenchmarkRunner` SHALL create a `JudgeClient` at initialization when a judge is configured and pass it to the `Scorer`.

The runner SHALL:
- Load the judge profile from config and instantiate the model client
- Create a `Scorer` with the `JudgeClient`
- Pass the judge-enabled scorer to benchmarks during fixture execution

#### Scenario: Runner with judge configuration
- **WHEN** the runner is initialized with a config containing a valid `judge` section with benchmarks including `commit_messages`
- **THEN** the runner SHALL create a `JudgeClient` from the specified profile and pass it to the `Scorer`

#### Scenario: Runner without judge configuration
- **WHEN** the runner is initialized without a `judge` section in config
- **THEN** the runner SHALL create a `Scorer` without a `JudgeClient`
