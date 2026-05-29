## MODIFIED Requirements

### Requirement: Model name supports #level suffix
Model names in profiles, CLI, and all configuration contexts SHALL support an optional GitBench effort suffix that specifies the effort level for that run target. The suffix MAY use `#<level>` or `:<level>`. A final colon segment SHALL be treated as effort only when it exactly matches a valid GitBench effort value. Valid effort values SHALL be `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, and `max`.

#### Scenario: Model name with hash effort level
- **WHEN** a profile lists `"o3-mini#high"` as a model
- **THEN** the base model name is `"o3-mini"` and the reasoning level is `"high"`

#### Scenario: Model name with colon effort level
- **WHEN** a profile lists `"anthropic/claude-opus-4.7:max"` as a model
- **THEN** the base model name is `"anthropic/claude-opus-4.7"` and the reasoning level is `"max"`

#### Scenario: Model name without reasoning level
- **WHEN** a profile lists `"gpt-4o-mini"` as a model
- **THEN** the base model name is `"gpt-4o-mini"` and the reasoning level is `None`

#### Scenario: Model name with multiple # characters
- **WHEN** a model name is `"model#a#b"`
- **THEN** only the last `#` SHALL be used as delimiter: base model is `"model#a"` and reasoning level is `"b"`

#### Scenario: Colon model tag that is not an effort
- **WHEN** a model name is `"llama3.1:8b"`
- **THEN** the base model name is `"llama3.1:8b"` and the reasoning level is `None`

#### Scenario: Colon effort after model tag
- **WHEN** a model name is `"llama3.1:8b:high"`
- **THEN** the base model name is `"llama3.1:8b"` and the reasoning level is `"high"`

#### Scenario: Anthropic max effort is valid
- **WHEN** a profile lists `"anthropic/claude-opus-4.7:max"` as a model
- **THEN** model validation accepts the `max` effort level

### Requirement: Adapters parse model name
Each adapter SHALL parse the model name at construction time, storing the base model name for API calls and the reasoning level for forwarding or recording. Capacity grouping SHALL use the parsed base model name, not the full model name with effort.

#### Scenario: OpenAI adapter parses model with level
- **WHEN** `OpenAIAdapter(model="o3-mini#high")` is constructed
- **THEN** `self.model` is `"o3-mini"` and `self.reasoning_level` is `"high"`

#### Scenario: OpenRouter-compatible adapter parses colon effort
- **WHEN** `OpenAIAdapter(model="anthropic/claude-opus-4.7:max", base_url="https://openrouter.ai/api/v1")` is constructed
- **THEN** `self.model` is `"anthropic/claude-opus-4.7"` and `self.reasoning_level` is `"max"`

#### Scenario: Ollama adapter parses model with level
- **WHEN** `OllamaAdapter(model="llama3.1#medium")` is constructed
- **THEN** `self.model` is `"llama3.1"` and `self.reasoning_level` is `"medium"`

#### Scenario: Adapter preserves model name for display
- **WHEN** an adapter is constructed with `"o3-mini#high"`
- **THEN** the adapter SHALL store the original full model name for use in result metadata

#### Scenario: Capacity identity excludes effort
- **WHEN** an adapter is constructed with `"anthropic/claude-opus-4.7:max"`
- **THEN** scheduler capacity grouping uses `"anthropic/claude-opus-4.7"` as the base model ID
