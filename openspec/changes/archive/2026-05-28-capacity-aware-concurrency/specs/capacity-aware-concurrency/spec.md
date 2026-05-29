## ADDED Requirements

### Requirement: Model API calls are gated by request budgets
GitBench SHALL gate each real model API call through a global request budget and a capacity-group request budget before invoking `ModelInterface.generate()`.

#### Scenario: Global request budget limits simultaneous calls
- **WHEN** a run schedules work for multiple models and fixtures with a global maximum of 2 concurrent requests
- **THEN** no more than 2 model API calls are in progress at the same time

#### Scenario: Capacity group request budget limits simultaneous calls
- **WHEN** two scheduled fixtures target models in the same capacity group with `max_concurrent_requests` set to 1
- **THEN** the second model API call waits until the first model API call releases the group permit

#### Scenario: Independent groups may run concurrently
- **WHEN** two scheduled fixtures target models in different capacity groups and the global request budget has available permits
- **THEN** both model API calls may run at the same time

### Requirement: Capacity grouping ignores GitBench effort
GitBench SHALL derive capacity groups from the base model ID after removing any GitBench effort suffix.

#### Scenario: Effort variants share capacity group
- **WHEN** a profile contains `openai/gpt-5.4-mini:low` and `openai/gpt-5.4-mini:max`
- **THEN** both run targets use the same capacity group

#### Scenario: Effort remains in result identity
- **WHEN** a run target `anthropic/claude-opus-4.7:max` completes
- **THEN** result metadata and progress labels still identify the run target with effort `max`

### Requirement: OpenRouter groups are inferred from upstream model family
For OpenRouter profiles, GitBench SHALL infer capacity groups from the configured model string's upstream provider and model family after effort stripping.

#### Scenario: Anthropic Opus versions share a group
- **WHEN** an OpenRouter profile contains `anthropic/claude-opus-4.7:max` and `anthropic/claude-opus-4.8:max`
- **THEN** both run targets use the capacity group `openrouter:anthropic/claude-opus`

#### Scenario: Anthropic model families are separate
- **WHEN** an OpenRouter profile contains `anthropic/claude-opus-4.7:max` and `anthropic/claude-sonnet-4.7:max`
- **THEN** the Opus target uses `openrouter:anthropic/claude-opus` and the Sonnet target uses `openrouter:anthropic/claude-sonnet`

#### Scenario: OpenAI GPT variants share inferred family
- **WHEN** an OpenRouter profile contains `openai/gpt-5.4-mini:high` and `openai/gpt-5.4-nano:xhigh`
- **THEN** both run targets use the capacity group `openrouter:openai/gpt-5`

#### Scenario: Unknown OpenRouter family falls back to base model ID
- **WHEN** an OpenRouter model ID does not match a known family inference rule
- **THEN** GitBench uses `openrouter:<base-model-id>` as the inferred capacity group

### Requirement: Explicit concurrency groups override inference
GitBench SHALL allow config-defined concurrency groups to override inferred capacity groups. Override matching SHALL apply to the base model ID after effort stripping.

#### Scenario: Explicit group collapses matching models
- **WHEN** config defines a group with key `openrouter:anthropic/claude` matching `anthropic/claude-*`
- **THEN** `anthropic/claude-opus-4.7:max` and `anthropic/claude-sonnet-4.7:high` both use `openrouter:anthropic/claude`

#### Scenario: Explicit group limit is used
- **WHEN** a matched explicit group has `max_concurrent_requests` set to 1
- **THEN** GitBench uses 1 as the request budget for that capacity group

#### Scenario: Explicit groups do not match effort suffixes
- **WHEN** config defines a group matching `anthropic/claude-opus-*`
- **THEN** the group matches `anthropic/claude-opus-4.7:max` based on base model ID `anthropic/claude-opus-4.7`

### Requirement: Scheduling preserves deterministic output
GitBench SHALL preserve existing output structure and deterministic ordering even when scheduled work completes out of order.

#### Scenario: Model output order follows config order
- **WHEN** model runs complete in a different order than they were configured
- **THEN** stdout JSON, JSON output files, and JSONL records preserve configured model order

#### Scenario: Fixture output order follows fixture order
- **WHEN** fixtures complete in a different order than they were loaded
- **THEN** each benchmark result lists scores in fixture order
