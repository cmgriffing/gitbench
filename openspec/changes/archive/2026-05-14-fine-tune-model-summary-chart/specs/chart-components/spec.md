## MODIFIED Requirements

### Requirement: PassRateBarChart renders horizontal bar chart
The `PassRateBarChart` React component SHALL render a Recharts vertical bar chart (bars go up, X-axis = model, Y-axis = pass rate percentage). Bars SHALL be color-coded by provider using the `getProviderColor()` palette. X-axis tick labels SHALL be rotated diagonally (-40°) with a custom tick renderer that displays: a provider brand icon (via `ProviderIcon`), the truncated model name (max ~10 characters + ellipsis), and the reasoning level suffix. The component SHALL accept a `data` prop containing the full dataset and a `selectedModels` prop listing models to display. Chart height SHALL be fixed at 350 pixels. A provider legend SHALL be rendered below the chart card showing colored dots for each unique provider present.

#### Scenario: Bars render for selected models
- **WHEN** `PassRateBarChart` receives `selectedModels=['anthropic/claude-opus-4.7:low', 'openai/gpt-oss-120b:high']`
- **THEN** two vertical bars are displayed with the corresponding pass rates

#### Scenario: Colors reflect provider
- **WHEN** a model has provider `anthropic`
- **THEN** its bar is rendered in the Anthropic palette color (#D97757)

#### Scenario: Colors reflect provider for fallback providers
- **WHEN** a model has provider `unknown-provider`
- **THEN** its bar is rendered in a deterministic `hsl(hue, 55%, 48%)` color

#### Scenario: Diagonal labels show provider icon and truncated name
- **WHEN** a model name is `openai/gpt-oss-120b:high`
- **THEN** its X-axis tick shows the OpenAI icon, "gpt-oss-1…" (truncated), and "high" on a separate line, rotated -40°

#### Scenario: Long model names are truncated
- **WHEN** a model name exceeds ~10 characters in the base model part
- **THEN** the displayed label is truncated with an ellipsis

#### Scenario: Chart height is fixed at 350 pixels
- **WHEN** 5, 12, or 30 models are selected
- **THEN** the chart height is always 350 pixels

#### Scenario: Tick labels are offset below the axis line
- **WHEN** the chart renders with any model count
- **THEN** the X-axis tick labels appear below the horizontal axis line, not centered on it

#### Scenario: Provider legend appears below the chart
- **WHEN** the chart shows models from multiple providers
- **THEN** a horizontal legend with colored dots and provider names appears below the chart card
