## MODIFIED Requirements

### Requirement: PassRateBarChart renders horizontal bar chart
The `PassRateBarChart` React component SHALL render a Recharts vertical bar chart (bars go up, X-axis = provider/base-model group, Y-axis = pass rate percentage). Each bar SHALL represent one selected provider/base-model group and SHALL visualize the range from the lowest effort pass rate to the highest effort pass rate in that group. The highest effort pass rate SHALL be the representative value used for sorting and bar prominence. Bars SHALL be color-coded by provider using the `getProviderColor()` palette. X-axis tick labels SHALL be rotated diagonally (-40°) with a custom tick renderer that displays a provider brand icon (via `ProviderIcon`) and the truncated base model name (max ~10 characters + ellipsis). The component SHALL accept optional `benchmarkName` and `selectedBenchmark` props. When `benchmarkName` is provided, pass rates SHALL be computed from `matrix[model][benchmarkName].pass_at_k` (per-benchmark), otherwise from `model_summaries[model].pass_at_k` (global). The tooltip footnote SHALL reflect the data source — showing the fixture count for the benchmark when filtered, or "204 fixtures" for global. Chart height SHALL be fixed at 350 pixels. A provider legend SHALL be rendered below the chart card showing colored dots for each unique provider present.

#### Scenario: Bars render for selected model groups
- **WHEN** `PassRateBarChart` receives selected groups `['anthropic/claude-opus-4.7', 'openai/gpt-oss-120b']`
- **THEN** two vertical grouped bars are displayed with pass-rate ranges for the selected base models

#### Scenario: Effort range shown for a group
- **WHEN** `openai/gpt-5` has effort pass rates 72%, 81%, and 85%
- **THEN** the `openai/gpt-5` bar visualizes the range 72%-85% and uses 85% as the representative value

#### Scenario: Bars sorted by highest score
- **WHEN** grouped models have highest effort pass rates 90%, 75%, and 82%
- **THEN** bars appear ordered by 90%, 82%, then 75%

#### Scenario: Colors reflect provider
- **WHEN** a model group has provider `anthropic`
- **THEN** its bar is rendered in the Anthropic palette color (#D97757)

#### Scenario: Colors reflect provider for fallback providers
- **WHEN** a model group has provider `unknown-provider`
- **THEN** its bar is rendered in a deterministic `hsl(hue, 55%, 48%)` color

#### Scenario: Diagonal labels show provider icon and truncated base model
- **WHEN** a model group is `openai/gpt-oss-120b`
- **THEN** its X-axis tick shows the OpenAI icon and "gpt-oss-1…" (truncated), rotated -40°

#### Scenario: Long model names are truncated
- **WHEN** a base model name exceeds ~10 characters
- **THEN** the displayed label is truncated with an ellipsis

#### Scenario: Chart height is fixed at 350 pixels
- **WHEN** 5, 12, or 30 model groups are selected
- **THEN** the chart height is always 350 pixels

#### Scenario: Tick labels are offset below the axis line
- **WHEN** the chart renders with any model group count
- **THEN** the X-axis tick labels appear below the horizontal axis line, not centered on it

#### Scenario: Provider legend appears below the chart
- **WHEN** the chart shows model groups from multiple providers
- **THEN** a horizontal legend with colored dots and provider names appears below the chart card

#### Scenario: Per-benchmark pass rates used when benchmarkName provided
- **WHEN** `PassRateBarChart` receives `benchmarkName="blame_forensics"`
- **THEN** bars reflect pass rates from `matrix[model]["blame_forensics"].pass_at_k` with the tooltip footnote showing the number of fixtures in that benchmark

#### Scenario: Global pass rates used when benchmarkName absent
- **WHEN** `PassRateBarChart` renders without a `benchmarkName` prop
- **THEN** bars reflect pass rates from `model_summaries[model].pass_at_k` and the tooltip footnote reads "% of 204 fixtures passed"
