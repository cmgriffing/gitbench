## Purpose

Reasoning level forwarding defines how model adapters translate GitBench reasoning effort into provider-specific request parameters or intentionally ignore unsupported effort values.

## Requirements

### Requirement: OpenAIAdapter forwards reasoning level as reasoning_effort
When an `OpenAIAdapter` was constructed with a reasoning level, calls to `generate()` SHALL forward it using the transport-appropriate request shape. For the first-party OpenAI API, the adapter SHALL forward the value as `reasoning_effort`. For OpenRouter-compatible base URLs, non-`none` levels SHALL be forwarded as `reasoning.effort`, while `none` SHALL be forwarded as an explicit disabled reasoning configuration.

#### Scenario: OpenAI call with reasoning level from model name
- **WHEN** `OpenAIAdapter(model="o3-mini#high")` calls `generate()`
- **THEN** the `client.chat.completions.create()` call SHALL include `reasoning_effort="high"`

#### Scenario: OpenAI call with none
- **WHEN** `OpenAIAdapter(model="gpt-5.4#none")` calls `generate()` against the first-party OpenAI API
- **THEN** the call SHALL include `reasoning_effort="none"`

#### Scenario: OpenRouter call with max effort from model name
- **WHEN** `OpenAIAdapter(model="anthropic/claude-opus-4.7:max", base_url="https://openrouter.ai/api/v1")` calls `generate()`
- **THEN** the call SHALL include `reasoning={"effort": "max"}`

#### Scenario: OpenRouter call explicitly disables reasoning
- **WHEN** `OpenAIAdapter(model="some/model:none", base_url="https://openrouter.ai/api/v1")` calls `generate()`
- **THEN** the call SHALL include `reasoning={"enabled": false}` and SHALL NOT send `reasoning.effort="none"`

#### Scenario: OpenRouter reasoning preserves extra body
- **WHEN** an OpenRouter call includes caller-provided `extra_body` routing fields
- **THEN** the adapter SHALL merge the reasoning configuration without removing routing fields or mutating the caller-owned object

#### Scenario: OpenAI call without reasoning level
- **WHEN** `OpenAIAdapter(model="o3-mini")` calls `generate()`
- **THEN** the `client.chat.completions.create()` call SHALL NOT include reasoning controls

## ADDED Requirements

### Requirement: None responses contain verifiable zero reasoning
Every response produced by a model configured with reasoning level `none` SHALL explicitly report zero reasoning tokens and SHALL contain no non-empty reasoning content. The adapter SHALL raise a dedicated reasoning-disable error for violations. During preflight this error SHALL abort the run before benchmark fixtures start; during fixture execution it SHALL be recorded as an ordinary failed fixture score.

#### Scenario: None response reports zero reasoning
- **WHEN** a `none` response reports `reasoning_tokens: 0` and has no reasoning content
- **THEN** the response SHALL be accepted

#### Scenario: None response reports reasoning tokens
- **WHEN** a `none` response reports `reasoning_tokens` greater than zero
- **THEN** the adapter SHALL raise a reasoning-disable error identifying the model and observed token count

#### Scenario: None response contains reasoning content
- **WHEN** a `none` response contains non-empty `reasoning`, `reasoning_content`, or equivalent normalized reasoning text
- **THEN** the adapter SHALL raise a reasoning-disable error

#### Scenario: None response omits reasoning telemetry
- **WHEN** a `none` response has no explicit reasoning-token count
- **THEN** the adapter SHALL raise a reasoning-disable error stating that the no-reasoning invariant could not be verified

#### Scenario: Runtime violation fails fixture
- **WHEN** a benchmark fixture response violates the `none` invariant after preflight succeeded
- **THEN** GitBench SHALL record the fixture as failed with the violation diagnostic and continue the benchmark run

### Requirement: OllamaAdapter ignores reasoning level
When an `OllamaAdapter` was constructed with a reasoning level, calls to `generate()` SHALL log a debug message and NOT include the level in the request.

#### Scenario: Ollama call with reasoning level from model name
- **WHEN** `OllamaAdapter(model="llama3.1#medium")` calls `generate()`
- **THEN** a debug-level log message SHALL be emitted and the request body SHALL NOT include reasoning parameters

#### Scenario: Ollama call without reasoning level
- **WHEN** `OllamaAdapter(model="llama3.1")` calls `generate()`
- **THEN** no debug message about reasoning SHALL be logged and the request SHALL proceed normally

### Requirement: MockModelClient ignores reasoning level
The `MockModelClient` SHALL silently accept and ignore the `#level` or `:level` suffix in model names.

#### Scenario: Mock with reasoning level
- **WHEN** `MockModelClient()` or `get_model_client("mock#high")` is used
- **THEN** mock behavior SHALL be unchanged and `call_count` SHALL increment normally

#### Scenario: Mock with max effort
- **WHEN** `get_model_client("mock:max")` is used
- **THEN** mock behavior SHALL be unchanged and `call_count` SHALL increment normally
