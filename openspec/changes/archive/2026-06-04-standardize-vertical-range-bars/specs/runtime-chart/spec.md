## ADDED Requirements

### Requirement: RuntimeBarChart renders vertical range-whisker bar chart ranking models by speed
The `RuntimeBarChart` React component SHALL render a Recharts vertical bar chart (bars go up, X-axis = provider/base-model group, Y-axis = total runtime in seconds). Each solid bar SHALL represent one selected provider/base-model group's representative effort runtime from zero. The representative runtime SHALL be the median value from the group's sorted, deduped effort runtimes. A neutral range whisker SHALL visualize the range from the fastest effort runtime to the slowest effort runtime in that group. The representative runtime SHALL be used for sorting and bar prominence. The Y-axis domain SHALL start at 0 and include the slowest displayed effort runtime. Bars SHALL be color-coded by provider using the `getProviderColor()` palette. X-axis tick labels SHALL display the provider brand icon (via `ProviderIcon`) and the truncated base model name (max ~10 characters + ellipsis), rotated `-40` degrees. The component SHALL accept a `data` prop containing the full dataset and an optional selected group list for filtering. Chart height SHALL be fixed at 350 pixels. A provider legend SHALL be rendered below the chart card showing colored dots for each unique provider present. Model groups SHALL be sorted fastest-first by their representative runtime.

#### Scenario: Bars render for selected model groups
- **WHEN** `RuntimeBarChart` receives selected groups `['anthropic/claude-opus-4.7', 'openai/gpt-oss-120b']`
- **THEN** two vertical grouped bars are displayed with runtime range whiskers for the selected base models

#### Scenario: Fastest representative grouped model appears first
- **WHEN** model groups have representative runtimes [5000, 12000, 3000, 8000]
- **THEN** bars appear from left to right in order: 3000, 5000, 8000, 12000

#### Scenario: Effort range shown with whisker
- **WHEN** `openai/gpt-5` has effort runtimes 45s, 70s, and 110s
- **THEN** the `openai/gpt-5` solid bar extends from 0s to 70s and its range whisker spans 45s-110s

#### Scenario: Duplicate effort runtimes are deduped before selecting representative runtime
- **WHEN** `openai/gpt-5` has effort runtimes 45s, 45s, 45s, 70s, and 110s
- **THEN** the `openai/gpt-5` representative runtime is 70s from deduped values [45s, 70s, 110s]

#### Scenario: Colors reflect provider
- **WHEN** a model group has provider `anthropic`
- **THEN** its bar is rendered in the Anthropic palette color (#D97757)

#### Scenario: Colors reflect provider for fallback providers
- **WHEN** a model group has provider `unknown-provider`
- **THEN** its bar is rendered in a deterministic `hsl(hue, 55%, 48%)` color

#### Scenario: Diagonal labels show provider icon and truncated base model
- **WHEN** a model group is `openai/gpt-oss-120b`
- **THEN** its X-axis tick shows the OpenAI icon and "gpt-oss-1..." (truncated), rotated `-40` degrees

#### Scenario: Long model names are truncated
- **WHEN** a base model name exceeds ~10 characters
- **THEN** the displayed label is truncated with an ellipsis

#### Scenario: Chart height is fixed at 350 pixels
- **WHEN** 5, 12, or 30 model groups are present
- **THEN** the chart height is always 350 pixels

#### Scenario: Provider legend appears below the chart
- **WHEN** the chart shows model groups from multiple providers
- **THEN** a horizontal legend with colored dots and provider names appears below the chart card

## MODIFIED Requirements

### Requirement: RuntimeBarChart reads from model_runtimes in aggregated data
The `RuntimeBarChart` component SHALL read runtime data from `data.model_runtimes[modelName].total_ms`. It SHALL convert milliseconds to seconds for display (dividing by 1000). The Y-axis SHALL be labeled in seconds (e.g., "120s", "45.3s").

#### Scenario: Total runtime converted to seconds
- **WHEN** a model has `total_ms=45300`
- **THEN** the bar represents 45.3 seconds and the Y-axis tick shows "45.3s"

#### Scenario: Zero millisecond total handled
- **WHEN** a model has `total_ms=0`
- **THEN** the bar represents 0 seconds and the Y-axis tick shows "0s"

### Requirement: RuntimeBarChart is placed on Models overview page
The `RuntimeBarChart` component SHALL be rendered on `/` (the Overview/Home page) after the Cost per Full Run section, in its own section labeled "Runtime (Wall Clock)". It SHALL be loaded with `client:load`.

#### Scenario: Chart on overview page
- **WHEN** navigating to `/`
- **THEN** a "Runtime (Wall Clock)" section with the grouped vertical range-whisker bar chart is visible

## REMOVED Requirements

### Requirement: RuntimeBarChart renders horizontal bar chart ranking models by speed
**Reason**: Replaced by the shared vertical representative-bar plus range-whisker chart language.
**Migration**: Use `RuntimeBarChart renders vertical range-whisker bar chart ranking models by speed`.
