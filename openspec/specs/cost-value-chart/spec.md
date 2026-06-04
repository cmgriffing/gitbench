## Purpose

The CostValueChart provides a quadrant scatter plot comparing each model's total cost against its pass rate.
## Requirements
### Requirement: CostValueChart shows tooltips on hover

Hovering over a grouped cost bar SHALL display a tooltip with the provider/base-model group name, each effort's total cost formatted as USD (e.g., "$0.5270" or "$12.50"), and each effort's pass rate percentage for context. The tooltip SHALL identify the lowest-cost effort used for sorting.

#### Scenario: Tooltip on hover
- **WHEN** a user hovers over a grouped cost bar
- **THEN** a tooltip appears showing the provider/base-model group name, total cost for each effort, and pass rate percentage for each effort

#### Scenario: Tooltip identifies lowest-cost effort
- **WHEN** one effort has the lowest total cost in a grouped cost bar
- **THEN** the tooltip identifies that effort as the value used for sorting

### Requirement: CostValueChart handles models without cost data

Child efforts with no cost data (`total_cost_usd` is null) SHALL NOT contribute to their model group's cost range or tooltip. If a selected model group has no child efforts with cost data, that group SHALL NOT appear on the chart. If ALL selected model groups lack cost data, the component SHALL display a message: "No pricing data available."

#### Scenario: Effort without cost is excluded
- **WHEN** one effort in a selected model group has null `total_cost_usd` and other efforts have valid costs
- **THEN** only the efforts with valid costs contribute to that group's cost range

#### Scenario: Group without cost is excluded
- **WHEN** a selected model group has no efforts with valid `total_cost_usd`
- **THEN** that group does not appear as a bar

#### Scenario: All selected groups lack cost data
- **WHEN** every selected model group lacks valid `total_cost_usd`
- **THEN** the chart area displays "No pricing data available"

### Requirement: CostValueChart is placed on Models overview page

The `CostValueChart` component SHALL be rendered on `/` (the Overview/Home page) inside a section labeled "Cost per Full Run". It SHALL be loaded with `client:load`.

#### Scenario: Chart on overview page
- **WHEN** navigating to `/`
- **THEN** a "Cost per Full Run" section with the grouped vertical range-whisker bar chart is visible

### Requirement: CostValueChart bars navigate to model detail

Clicking a grouped bar SHALL navigate the browser to `/models/<provider>/<base-model>/`.

#### Scenario: Click navigates to base model detail
- **WHEN** a user clicks on the grouped bar for model group `anthropic/claude-opus-4.7`
- **THEN** the browser navigates to `/models/anthropic/claude-opus-4.7/`

### Requirement: CostValueChart includes ModelSelector filter

The `CostValueChart` component SHALL include a `ModelSelector` dropdown allowing users to filter which provider/base-model groups appear in the chart. The selector SHALL use the shared Overview model group selection state. When any other Overview chart selector changes the selected group set, `CostValueChart` SHALL update its rendered bars and provider legend from that same selected group set. Groups without cost data SHALL remain excluded from the rendered bars even when selected.

#### Scenario: Filter removes model group from chart
- **WHEN** a user deselects a model group in the ModelSelector
- **THEN** that model group's bar is removed from the chart

#### Scenario: External selection updates cost chart
- **WHEN** a user changes the selected model groups in another Overview chart's ModelSelector
- **THEN** `CostValueChart` updates its bars to match the new selected group set, excluding selected groups without cost data

#### Scenario: Selector remains available when no selected groups have cost data
- **WHEN** the selected group set contains no model groups with valid `total_cost_usd`
- **THEN** `CostValueChart` displays "No pricing data available" and still renders the ModelSelector

### Requirement: CostValueChart renders vertical range-whisker bar chart

The `CostValueChart` React component SHALL render a Recharts vertical bar chart (bars go up, X-axis = provider/base-model group, Y-axis = total cost in USD). Each solid bar SHALL represent one selected provider/base-model group's representative effort total cost from zero using `summary.total_cost_usd` from model summaries. The representative cost SHALL be the median value from the group's sorted, deduped effort costs. A neutral range whisker SHALL visualize the range from the lowest effort total cost to the highest effort total cost in that group. The representative cost SHALL be used for sorting and bar prominence. The Y-axis domain SHALL start at 0 and include the highest displayed effort cost. Bars SHALL be color-coded by provider using the `getProviderColor()` palette. X-axis tick labels SHALL display the provider brand icon (via `ProviderIcon`) and the truncated base model name (max ~10 characters + ellipsis), rotated `-40` degrees. The component SHALL accept a `data` prop containing the full dataset. Chart height SHALL be fixed at 350 pixels. A provider legend SHALL be rendered below the chart card showing colored dots for each unique provider present.

#### Scenario: One bar per model group
- **WHEN** `CostValueChart` renders with 5 selected model groups
- **THEN** 5 vertical grouped bars appear representing each model group's representative cost with range whiskers

#### Scenario: Bars sorted by representative cost
- **WHEN** model groups have representative costs [0.10, 0.20, 0.50, 0.80, 1.00]
- **THEN** bars appear from left to right in ascending order from lowest representative cost to highest

#### Scenario: Effort range shown with whisker
- **WHEN** `openai/gpt-5` has effort costs $0.10, $0.20, and $0.50
- **THEN** the `openai/gpt-5` solid bar extends from $0 to $0.20 and its range whisker spans $0.10-$0.50

#### Scenario: Duplicate effort costs are deduped before selecting representative cost
- **WHEN** `openai/gpt-5` has effort costs $0.10, $0.10, $0.10, $0.20, and $0.50
- **THEN** the `openai/gpt-5` representative cost is $0.20 from deduped values [$0.10, $0.20, $0.50]

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

