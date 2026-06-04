## ADDED Requirements

### Requirement: Overview grouped metric charts use vertical range-whisker bars
Overview grouped metric bar charts SHALL use a shared vertical chart language for pass rate, cost, runtime, and token usage. Each chart SHALL place provider/base-model groups on the X-axis and the metric value on the Y-axis. The provider-colored solid bar SHALL start at zero and end at the chart's representative effort value, computed as the median of deduped effort values for that group. A neutral range whisker SHALL show the full effort range from `minValue` to `maxValue`. Range whiskers SHALL NOT be described as error bars in user-facing copy or specs.

#### Scenario: Solid bar shows representative value
- **WHEN** a grouped metric row has deduped effort values `[72, 81, 85]`, `minValue=72`, and `maxValue=85`
- **THEN** the solid bar extends from 0 to 81 and the range whisker spans 72 to 85

#### Scenario: Lower-is-better metric uses median value as bar height
- **WHEN** a grouped metric row for cost has effort values `$0.10`, `$0.20`, and `$0.50`
- **THEN** the solid bar extends from 0 to `$0.20` and the range whisker spans `$0.10` to `$0.50`

#### Scenario: Duplicate values do not overweight the median
- **WHEN** a grouped metric row has effort values `[10, 10, 10, 20, 50]`
- **THEN** the representative effort value is computed from deduped values `[10, 20, 50]`, so the solid bar extends from 0 to 20 and the range whisker spans 10 to 50

#### Scenario: Numeric axis starts at zero
- **WHEN** any grouped metric chart renders
- **THEN** its numeric Y-axis lower bound is 0

#### Scenario: Diagonal group labels are reused
- **WHEN** any grouped metric chart renders an X-axis tick
- **THEN** the tick uses the existing diagonal provider-icon label pattern with `-40` degree rotation and a truncated base model name

#### Scenario: Single-effort groups remain visible
- **WHEN** a grouped metric row has `minValue`, `maxValue`, and `representativeValue` all equal
- **THEN** the solid bar remains visible from 0 to the representative value and the range whisker may collapse or be omitted

### Requirement: PassRateBarChart renders vertical range-whisker bar chart
The `PassRateBarChart` React component SHALL render a Recharts vertical bar chart (bars go up, X-axis = provider/base-model group, Y-axis = pass rate percentage). Each solid bar SHALL represent one selected provider/base-model group's median deduped effort pass rate from zero. A neutral range whisker SHALL visualize the range from the lowest effort pass rate to the highest effort pass rate in that group. The median deduped effort pass rate SHALL be the representative value used for sorting and bar prominence. The Y-axis domain SHALL start at 0 and SHALL use 100 as the pass-rate ceiling. Bars SHALL be color-coded by provider using the `getProviderColor()` palette. X-axis tick labels SHALL be rotated diagonally (`-40` degrees) with a custom tick renderer that displays a provider brand icon (via `ProviderIcon`) and the truncated base model name (max ~10 characters + ellipsis). The component SHALL accept optional `benchmarkName` and `selectedBenchmark` props. When `benchmarkName` is provided, pass rates SHALL be computed from `matrix[model][benchmarkName].pass_at_k` (per-benchmark), otherwise from `model_summaries[model].pass_at_k` (global). The tooltip footnote SHALL reflect the data source by showing the fixture count for the benchmark when filtered, or "204 fixtures" for global. Chart height SHALL be fixed at 350 pixels. A provider legend SHALL be rendered below the chart card showing colored dots for each unique provider present.

#### Scenario: Bars render for selected model groups
- **WHEN** `PassRateBarChart` receives selected groups `['anthropic/claude-opus-4.7', 'openai/gpt-oss-120b']`
- **THEN** two vertical grouped bars are displayed with range whiskers for the selected base models

#### Scenario: Effort range shown with whisker
- **WHEN** `openai/gpt-5` has effort pass rates 72%, 81%, and 85%
- **THEN** the `openai/gpt-5` solid bar extends from 0% to 81% and its range whisker spans 72%-85%

#### Scenario: Bars sorted by median score
- **WHEN** grouped models have median effort pass rates 90%, 75%, and 82%
- **THEN** bars appear ordered by 90%, 82%, then 75%

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

### Requirement: RuntimeBarChart renders vertical range-whisker bar chart ranking models by speed
The `RuntimeBarChart` React component SHALL render a Recharts vertical bar chart (bars go up, X-axis = provider/base-model group, Y-axis = total runtime in seconds). Each solid bar SHALL represent one selected provider/base-model group's median deduped effort runtime from zero. A neutral range whisker SHALL visualize the range from the fastest effort runtime to the slowest effort runtime in that group. The median deduped effort runtime SHALL be the representative value used for sorting and bar prominence. The Y-axis domain SHALL start at 0 and include the slowest displayed effort runtime. Bars SHALL be color-coded by provider using the `getProviderColor()` palette. X-axis tick labels SHALL display the provider brand icon (via `ProviderIcon`) and the truncated base model name (max ~10 characters + ellipsis), rotated `-40` degrees. The component SHALL accept a `data` prop containing the full dataset and an optional selected group list for filtering. Chart height SHALL be fixed at 350 pixels. A provider legend SHALL be rendered below the chart card showing colored dots for each unique provider present. Model groups SHALL be sorted fastest-first by their median deduped effort runtime.

#### Scenario: Bars render for selected model groups
- **WHEN** `RuntimeBarChart` receives selected groups `['anthropic/claude-opus-4.7', 'openai/gpt-oss-120b']`
- **THEN** two vertical grouped bars are displayed with runtime range whiskers for the selected base models

#### Scenario: Fastest median grouped model appears first
- **WHEN** model groups have median effort runtimes [5000, 12000, 3000, 8000]
- **THEN** bars appear from left to right in order: 3000, 5000, 8000, 12000

#### Scenario: Effort range shown for runtime
- **WHEN** `openai/gpt-5` has effort runtimes 45s, 70s, and 110s
- **THEN** the `openai/gpt-5` solid bar extends from 0s to 70s and its range whisker spans 45s-110s

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

## REMOVED Requirements

### Requirement: PassRateBarChart renders horizontal bar chart
**Reason**: Replaced by the shared vertical representative-bar plus range-whisker chart language.
**Migration**: Use `PassRateBarChart renders vertical range-whisker bar chart`.

### Requirement: RuntimeBarChart renders horizontal bar chart ranking models by speed
**Reason**: Replaced by the shared vertical representative-bar plus range-whisker chart language.
**Migration**: Use `RuntimeBarChart renders vertical range-whisker bar chart ranking models by speed`.
