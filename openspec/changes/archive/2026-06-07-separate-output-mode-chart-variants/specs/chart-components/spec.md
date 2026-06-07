## ADDED Requirements

### Requirement: All output-mode-aware bar charts pair text and JSON results
Every web bar chart that can display text and JSON-schema results SHALL render those modes as a visually grouped sibling pair when `Both` is selected. The current covered bar-chart uses SHALL include the overview pass-rate chart, benchmark leaderboard pass-rate chart, cost chart, API-time chart, token-usage chart, Compare overall pass-rate chart, and Compare per-benchmark chart. Text and JSON bars SHALL preserve the chart's existing base color meaning while using the shared solid-text and translucent-outlined-JSON treatments. Hovering or keyboard-focusing either sibling SHALL open one tooltip scoped to the shared model or model-effort identity, with separate `Text` and `JSON` sections. A single-mode selection SHALL render only the selected mode without an empty sibling slot.

#### Scenario: Overview metric charts use paired modes
- **WHEN** `Both` is selected on the overview page
- **THEN** pass rate, cost, API time, and token usage render text and JSON as sibling bars for each model category

#### Scenario: Benchmark leaderboard uses paired modes
- **WHEN** `Both` is selected on a benchmark detail page
- **THEN** its pass-rate leaderboard renders text and JSON as sibling bars for each model category

#### Scenario: Compare overall uses paired modes
- **WHEN** `Both` is selected on the Compare page
- **THEN** the overall pass-rate chart renders one canonical model-effort category with sibling text and JSON bars instead of separate variant categories

#### Scenario: Compare by benchmark uses paired model series
- **WHEN** `Both` is selected on the Compare page
- **THEN** the per-benchmark chart renders each canonical model effort's text and JSON bars consecutively as one visual pair

#### Scenario: Siblings share one scoped tooltip
- **WHEN** a user hovers either bar in any text/JSON pair
- **THEN** the tooltip is scoped to that pair's model or model-effort identity and separates the two output modes into distinct sections

#### Scenario: Single mode does not reserve a pair
- **WHEN** `Text` or `JSON` is selected
- **THEN** every covered bar chart renders one bar per visible model identity without an empty sibling slot

### Requirement: Quadrant chart separates text and JSON points
The `QuadrantComparisonChart` SHALL render output modes as separate points when `Both` is selected. For each selected provider/base-model group, the chart SHALL choose the highest-composite effort independently in text mode and JSON-schema mode, producing up to two points that share the same normalized metric domains. Text points SHALL use a solid provider-colored circle. JSON points SHALL use a translucent provider-colored fill with a visible provider-colored outline. When both points are available, a subtle neutral connector SHALL join their exact coordinates behind the points. Hovering or keyboard-focusing either point SHALL open one tooltip for the provider/base-model pair with separate `Text` and `JSON` sections. The ranked list and "Best blend" result SHALL rank output-mode points independently and identify their mode.

#### Scenario: Both mode shows two independently selected points
- **WHEN** a base model's best text effort and best JSON effort both have the selected X and Y metrics
- **THEN** `Both` mode renders one text point and one JSON point at their respective metric coordinates

#### Scenario: Different reasoning efforts can represent the modes
- **WHEN** the best text composite belongs to `high` effort and the best JSON composite belongs to `medium` effort
- **THEN** the paired points use those different reasoning efforts
- **AND** the tooltip identifies the effort selected for each mode

#### Scenario: Pair shares normalized domains
- **WHEN** text and JSON points are visible together
- **THEN** both modes are normalized against the same visible candidate ranges and plotted on the same X and Y domains

#### Scenario: Connector shows mode movement
- **WHEN** both output-mode points exist for a base model at different coordinates
- **THEN** a subtle neutral line connects their exact coordinates behind the points

#### Scenario: Coincident points remain distinguishable
- **WHEN** a base model's text and JSON points have identical X and Y values
- **THEN** the text point remains a solid circle and the JSON point remains visible as a larger outlined ring around it
- **AND** neither point's plotted coordinates are offset

#### Scenario: Either point opens one paired tooltip
- **WHEN** a user hovers or keyboard-focuses either point in a text/JSON pair
- **THEN** one tooltip shows separate `Text` and `JSON` sections with each mode's reasoning effort and raw X and Y metric values

#### Scenario: Missing mode remains visible and explicit
- **WHEN** `Both` is selected and a base model has a valid text point but no valid JSON point
- **THEN** the text point remains visible without a connector
- **AND** the tooltip's JSON section reads `No data`

#### Scenario: Single mode retains one point per base model
- **WHEN** `Text` or `JSON` is selected
- **THEN** the quadrant chart renders at most one best point per selected base model for that mode

#### Scenario: Ranking distinguishes output modes
- **WHEN** text and JSON points from the same base model both rank in the top six
- **THEN** both entries may appear and each entry identifies whether it is `Text` or `JSON`

#### Scenario: Best blend identifies mode
- **WHEN** the highest-composite visible point is a JSON point
- **THEN** the "Best blend" label identifies the base model and JSON mode

#### Scenario: Quadrant tooltip keeps no footnote
- **WHEN** the paired quadrant tooltip renders
- **THEN** it contains no separator and explanatory footnote

## MODIFIED Requirements

### Requirement: Overview grouped metric charts use vertical range-whisker bars
Overview grouped metric bar charts SHALL use a shared vertical chart language for pass rate, cost, API time, and token usage. Each chart SHALL place provider/base-model groups on the X-axis and the metric value on the Y-axis. For a single output-mode selection, each provider/base-model category SHALL render one provider-colored bar whose value is the median of the deduped effort values for that mode, with a neutral range whisker spanning that mode's minimum and maximum effort values. When `Both` is selected, each category SHALL render adjacent `Text` and `JSON` bars, and each bar SHALL use an independently computed median and range whisker from only that output mode's efforts. Text bars SHALL use the solid provider color. JSON bars SHALL use the same provider color with reduced fill opacity and a visible outline. Range whiskers SHALL NOT be described as error bars in user-facing copy or specs.

#### Scenario: Single mode shows one representative bar
- **WHEN** a grouped metric row in `Text` mode has deduped effort values `[72, 81, 85]`, `minValue=72`, and `maxValue=85`
- **THEN** one solid text bar extends from 0 to 81 and its range whisker spans 72 to 85

#### Scenario: Both mode shows independent sibling bars
- **WHEN** a model group has text effort values `[72, 81, 85]` and JSON effort values `[76, 88, 91]` while `Both` is selected
- **THEN** the category shows a text bar at 81 with a 72-85 whisker and an adjacent JSON bar at 88 with a 76-91 whisker

#### Scenario: Modes are not combined for the representative
- **WHEN** text effort values are `[10, 20]` and JSON effort values are `[80, 90]`
- **THEN** the text representative is 15 and the JSON representative is 85
- **AND** no displayed representative is calculated from the combined values `[10, 20, 80, 90]`

#### Scenario: Duplicate values do not overweight each mode median
- **WHEN** one output mode has effort values `[10, 10, 10, 20, 50]`
- **THEN** that mode's representative value is computed from deduped values `[10, 20, 50]`, so its bar extends from 0 to 20 and its whisker spans 10 to 50

#### Scenario: Numeric axis starts at zero
- **WHEN** any grouped metric chart renders
- **THEN** its numeric Y-axis lower bound is 0

#### Scenario: Diagonal group labels are reused for pairs
- **WHEN** a grouped metric chart renders paired text and JSON bars
- **THEN** both bars share one existing diagonal provider-icon label with `-40` degree rotation and a truncated base model name

#### Scenario: Single-effort mode remains visible
- **WHEN** one mode summary has equal minimum, maximum, and representative values
- **THEN** that mode's bar remains visible from 0 to the representative value and its range whisker may collapse or be omitted

#### Scenario: Missing sibling mode preserves the category
- **WHEN** `Both` is selected and a provider/base-model group has text data but no JSON data
- **THEN** the text bar renders in its normal sibling position, the JSON slot remains empty, and the model category remains on the chart

#### Scenario: Both mode includes a style legend
- **WHEN** a grouped metric chart renders with `Both` selected
- **THEN** a mode legend identifies the solid treatment as `Text` and the translucent outlined treatment as `JSON`

### Requirement: PassRateBarChart renders vertical range-whisker bar chart
The `PassRateBarChart` React component SHALL render a Recharts vertical bar chart (bars go up, X-axis = provider/base-model group, Y-axis = pass rate percentage). For a single output-mode selection, each category SHALL show that mode's median deduped effort pass rate from zero with a neutral range whisker from its lowest to highest effort pass rate. When `Both` is selected, each category SHALL show adjacent text and JSON bars with independently calculated medians and range whiskers. The Y-axis domain SHALL start at 0 and SHALL use 100 as the pass-rate ceiling. Bars SHALL be color-coded by provider using the `getProviderColor()` palette and SHALL use the shared output-mode visual treatments. X-axis tick labels SHALL be rotated diagonally (`-40` degrees) with a custom tick renderer that displays a provider brand icon (via `ProviderIcon`) and the truncated base model name (max ~10 characters + ellipsis). The component SHALL accept optional `benchmarkName` and `selectedBenchmark` props. When `benchmarkName` is provided, pass rates SHALL be computed from `matrix[model][benchmarkName].pass_at_k` (per-benchmark), otherwise from `model_summaries[model].pass_at_k` (global). The tooltip footnote SHALL reflect the data source by showing the fixture count for the benchmark when filtered, or "204 fixtures" for global. Chart height SHALL be fixed at 350 pixels. A provider legend SHALL be rendered below the chart card showing colored dots for each unique provider present.

#### Scenario: Both mode renders paired pass-rate bars
- **WHEN** `Both` is selected for model groups `['anthropic/claude-opus-4.7', 'openai/gpt-oss-120b']`
- **THEN** each model category displays adjacent text and JSON pass-rate bars where those modes are available

#### Scenario: Effort ranges are independent by mode
- **WHEN** `openai/gpt-5` has text pass rates 72%, 81%, and 85% and JSON pass rates 76%, 88%, and 91%
- **THEN** the text bar extends to 81% with a 72%-85% whisker and the JSON bar extends to 88% with a 76%-91% whisker

#### Scenario: Single-mode rendering remains one bar
- **WHEN** the output-mode selection is `JSON`
- **THEN** each displayed model category contains one JSON bar and no reserved text bar

#### Scenario: Bars sorted by visible representative score
- **WHEN** a single output mode is selected and grouped models have representative pass rates 90%, 75%, and 82%
- **THEN** categories appear ordered by 90%, 82%, then 75%

#### Scenario: Both mode sorts by mean representative score
- **WHEN** `Both` is selected and two groups have text/JSON representatives `[90%, 70%]` and `[78%, 76%]`
- **THEN** the first group sorts ahead of the second because their mean representative scores are 80% and 77%

#### Scenario: Colors reflect provider
- **WHEN** a model group has provider `anthropic`
- **THEN** both of its mode bars use the Anthropic palette color (#D97757) with their respective mode treatments

#### Scenario: Colors reflect provider for fallback providers
- **WHEN** a model group has provider `unknown-provider`
- **THEN** its mode bars use a deterministic `hsl(hue, 55%, 48%)` provider color

#### Scenario: Diagonal labels show provider icon and truncated base model
- **WHEN** a model group is `openai/gpt-oss-120b`
- **THEN** its shared X-axis tick shows the OpenAI icon and "gpt-oss-1..." (truncated), rotated `-40` degrees

#### Scenario: Chart height is fixed at 350 pixels
- **WHEN** 5, 12, or 30 model groups are selected in single or both mode
- **THEN** the chart height is always 350 pixels

#### Scenario: Provider and mode legends appear below the chart
- **WHEN** the chart shows multiple providers with `Both` selected
- **THEN** the provider legend identifies provider colors and the mode legend identifies text and JSON bar treatments

#### Scenario: Either sibling triggers one separated tooltip
- **WHEN** a user hovers or keyboard-focuses either bar in a paired pass-rate category
- **THEN** one tooltip appears for the provider/base-model group with separate `Text` and `JSON` effort lists and a representative median for each available mode

#### Scenario: Missing mode is explicit in tooltip
- **WHEN** `Both` is selected and a category has text pass-rate data but no JSON pass-rate data
- **THEN** the shared tooltip shows the text effort list and a JSON section labeled `No data`

#### Scenario: Per-benchmark pass rates used when benchmarkName provided
- **WHEN** `PassRateBarChart` receives `benchmarkName="blame_forensics"`
- **THEN** both mode summaries use pass rates from `matrix[model]["blame_forensics"].pass_at_k` and the tooltip footnote shows that benchmark's fixture count

#### Scenario: Global pass rates used when benchmarkName absent
- **WHEN** `PassRateBarChart` renders without a `benchmarkName` prop
- **THEN** mode summaries use `model_summaries[model].pass_at_k` and the tooltip footnote reads "% of 204 fixtures passed"
