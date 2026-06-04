## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: CostValueChart is placed on Models overview page

The `CostValueChart` component SHALL be rendered on `/` (the Overview/Home page) inside a section labeled "Cost per Full Run". It SHALL be loaded with `client:load`.

#### Scenario: Chart on overview page
- **WHEN** navigating to `/`
- **THEN** a "Cost per Full Run" section with the grouped vertical range-whisker bar chart is visible

## REMOVED Requirements

### Requirement: CostValueChart renders horizontal bar chart
**Reason**: Replaced by the shared vertical representative-bar plus range-whisker chart language.
**Migration**: Use `CostValueChart renders vertical range-whisker bar chart`.
