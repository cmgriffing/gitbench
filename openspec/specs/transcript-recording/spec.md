# transcript-recording Specification

## Purpose
TBD - created by archiving change record-model-metadata. Update Purpose after archive.
## Requirements
### Requirement: Model adapters return full conversation transcript

The `ModelInterface.generate()` return dict SHALL include an optional `transcript` field containing the full conversation as a list of message dicts. The transcript SHALL include every message sent to the model (with `role` and `content`) followed by the assistant's response. When the API returns reasoning content separate from the final answer, the assistant entry SHALL include an optional `reasoning_content` key.

#### Scenario: OpenAI adapter builds transcript from messages and response
- **WHEN** `OpenAIAdapter.generate()` is called with two messages `[{"role": "user", "content": "hello"}]`
- **AND** the API returns `content: "hi there"` and `reasoning_content: "The user said hello, I should greet them back"`
- **THEN** the return dict's `transcript` is `[{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi there", "reasoning_content": "The user said hello, I should greet them back"}]`

#### Scenario: OpenAI adapter transcript omits reasoning_content when absent
- **WHEN** `OpenAIAdapter.generate()` receives a response with no `reasoning_content` on the message
- **THEN** the assistant entry in `transcript` has only `role` and `content` keys (no `reasoning_content`)

#### Scenario: Ollama adapter builds transcript from messages and response
- **WHEN** `OllamaAdapter.generate()` is called with a user message
- **THEN** the return dict's `transcript` contains the input messages followed by an assistant entry with the response content

#### Scenario: Mock adapter builds transcript from messages and fixed response
- **WHEN** `MockModelClient.generate()` is called with messages
- **THEN** the return dict's `transcript` contains all input messages followed by `{"role": "assistant", "content": "<mock response>"}`

### Requirement: Score dataclass stores transcript

The `Score` dataclass SHALL have an optional `transcript: list[dict] | None` field with a default of `None`. The `to_dict()` method SHALL omit the field when it is `None`. The `from_dict()` method SHALL accept `transcript` when present and default to `None` when absent.

#### Scenario: transcript defaults to None
- **WHEN** a `Score` is created without specifying `transcript`
- **THEN** `score.transcript` is `None`

#### Scenario: to_dict omits None transcript
- **WHEN** `score.to_dict()` is called on a `Score` with `transcript=None`
- **THEN** the resulting dict does NOT contain a `transcript` key

#### Scenario: to_dict includes non-None transcript
- **WHEN** `score.to_dict()` is called on a `Score` with `transcript=[{"role": "user", "content": "x"}]`
- **THEN** the resulting dict contains `"transcript": [{"role": "user", "content": "x"}]`

#### Scenario: from_dict handles missing transcript
- **WHEN** `Score.from_dict()` is called with a dict that has no `transcript` key
- **THEN** the returned `Score` has `transcript=None`

### Requirement: Runner maps transcript from response to Score

The `BenchmarkRunner._run_fixture()` method SHALL extract `transcript` from the model response dict and assign it to `score.transcript`. When the response lacks the key or the model call fails, the field SHALL remain `None`.

#### Scenario: Transcript mapped from successful response
- **WHEN** `_run_fixture()` receives a response with a `transcript` key
- **THEN** `score.transcript` contains the full conversation list

#### Scenario: Transcript is None on error
- **WHEN** `_run_fixture()` catches an exception from the model call
- **THEN** `score.transcript` is `None`

#### Scenario: Transcript is None when response lacks key
- **WHEN** `_run_fixture()` receives a response dict without a `transcript` key
- **THEN** `score.transcript` is `None`

### Requirement: Transcript preserves full message history

The transcript SHALL include every message passed to `generate()`, not just the final user prompt. This includes any system messages or multi-turn history that the benchmark may construct.

#### Scenario: Multi-message transcript preserved
- **WHEN** a benchmark sends `[{"role": "system", "content": "You are a git expert"}, {"role": "user", "content": "commit message"}]`
- **THEN** the transcript contains both messages followed by the assistant response

### Requirement: Transcripts preserve structured-output context
When a model call uses schema-enforced JSON output, the recorded transcript SHALL preserve enough structured-output context to debug the request and response, including the output mode and schema name or fixture contract identifier.

#### Scenario: Structured transcript includes mode metadata
- **WHEN** a model adapter records a transcript for a JSON-schema mode request
- **THEN** the transcript metadata identifies the output mode as `json_schema`

#### Scenario: Structured transcript preserves assistant payload
- **WHEN** a JSON-schema mode response is recorded
- **THEN** the assistant entry preserves the raw assistant content returned by the provider
- **AND** the score payload can be inspected to see the parsed structured payload or structured-output error

