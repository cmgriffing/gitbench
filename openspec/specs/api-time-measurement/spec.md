# api-time-measurement Specification

## Purpose
TBD - created by archiving change record-model-metadata. Update Purpose after archive.
## Requirements
### Requirement: Model adapters measure and return API call duration

The `ModelInterface.generate()` return dict SHALL include an optional `api_duration_ms` field representing the duration of the successful API call in milliseconds, measured with `time.perf_counter()`. This measurement SHALL span from immediately before the HTTP/API invocation until immediately after it returns, excluding any retry overhead or pre/post processing.

#### Scenario: OpenAI adapter measures API call duration
- **WHEN** `OpenAIAdapter.generate()` makes a successful `client.chat.completions.create()` call that takes 350ms
- **THEN** the return dict contains `"api_duration_ms"` with a value approximately 350.0

#### Scenario: OpenAI adapter measures only the successful attempt
- **WHEN** `OpenAIAdapter.generate()` retries twice (rate limit errors) then succeeds on the third attempt
- **THEN** `api_duration_ms` reflects only the third (successful) call's duration, not cumulative retry time

#### Scenario: OpenAI adapter timing uses high-resolution clock
- **WHEN** `OpenAIAdapter.generate()` measures API call duration
- **THEN** the measurement uses `time.perf_counter()` (monotonic, high-resolution)

#### Scenario: Ollama adapter measures API call duration
- **WHEN** `OllamaAdapter.generate()` makes a successful `/api/chat` call that takes 1200ms
- **THEN** the return dict contains `"api_duration_ms"` with a value approximately 1200.0

#### Scenario: Mock adapter simulates API call duration
- **WHEN** `MockModelClient.generate()` is called
- **THEN** the return dict contains `"api_duration_ms"` with a positive float reflecting the simulated latency (~10ms)

### Requirement: Score dataclass stores API duration

The `Score` dataclass SHALL have an optional `api_duration_ms: float | None` field with a default of `None`. The `to_dict()` method SHALL omit the field when it is `None`. The `from_dict()` method SHALL accept `api_duration_ms` when present and default to `None` when absent.

#### Scenario: api_duration_ms defaults to None
- **WHEN** a `Score` is created without specifying `api_duration_ms`
- **THEN** `score.api_duration_ms` is `None`

#### Scenario: to_dict omits None api_duration_ms
- **WHEN** `score.to_dict()` is called on a `Score` with `api_duration_ms=None`
- **THEN** the resulting dict does NOT contain an `api_duration_ms` key

#### Scenario: to_dict includes non-None api_duration_ms
- **WHEN** `score.to_dict()` is called on a `Score` with `api_duration_ms=350.2`
- **THEN** the resulting dict contains `"api_duration_ms": 350.2`

#### Scenario: from_dict handles missing api_duration_ms
- **WHEN** `Score.from_dict()` is called with a dict that has no `api_duration_ms` key
- **THEN** the returned `Score` has `api_duration_ms=None`

### Requirement: Runner maps API duration from response to Score

The `BenchmarkRunner._run_fixture()` method SHALL extract `api_duration_ms` from the model response dict and assign it to `score.api_duration_ms`. When the response lacks the key, the score field SHALL remain `None`.

#### Scenario: API duration mapped from successful response
- **WHEN** `_run_fixture()` receives a response with `"api_duration_ms": 350.2`
- **THEN** `score.api_duration_ms` is `350.2`

#### Scenario: API duration None when response lacks key
- **WHEN** `_run_fixture()` receives a response dict without an `api_duration_ms` key
- **THEN** `score.api_duration_ms` is `None`

### Requirement: API duration is distinct from wall-clock duration

The `api_duration_ms` field SHALL measure only the API call latency, while the existing `duration_ms` field SHALL continue to measure wall-clock time spanning setup, model call, scoring, and cleanup. Both metrics SHALL coexist on the same `Score` object.

#### Scenario: API duration is smaller than wall-clock duration
- **WHEN** a fixture run takes 2000ms wall-clock (`duration_ms`) and the API call takes 350ms (`api_duration_ms`)
- **THEN** `score.api_duration_ms` (350) is less than `score.duration_ms` (2000)

#### Scenario: Error path leaves api_duration_ms as None
- **WHEN** a fixture raises an exception before the model call completes
- **THEN** `score.api_duration_ms` is `None` while `score.duration_ms` may still be set (captured in finally block)

