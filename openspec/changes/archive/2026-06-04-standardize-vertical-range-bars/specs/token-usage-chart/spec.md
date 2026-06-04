## ADDED Requirements

### Requirement: TokenUsageChart renders vertical range-whisker bar chart

The `TokenUsageChart` React component SHALL render a Recharts vertical bar chart (bars go up, X-axis = provider/base-model group, Y-axis = total tokens). Each solid bar SHALL represent one selected provider/base-model group's representative effort token total from zero. The representative token total SHALL be the median value from the group's sorted, deduped effort token totals. A neutral range whisker SHALL visualize the range from the lowest effort token total to the highest effort token total in that group. The representative token total SHALL be used for sorting and bar prominence. The Y-axis domain SHALL start at 0 and include the highest displayed effort token total. Bars SHALL be color-coded by provider using the `getProviderColor()` palette. X-axis tick labels SHALL display the provider brand icon (via `ProviderIcon`) and the truncated base model name (max ~10 characters + ellipsis), rotated `-40` degrees. The component SHALL accept a `data` prop containing the full dataset. Chart height SHALL be fixed at 350 pixels. A provider legend SHALL be rendered below the chart card showing colored dots for each unique provider present.

#### Scenario: Bars render for selected model groups
- **WHEN** `TokenUsageChart` renders with 5 selected model groups
- **THEN** 5 vertical grouped bars are displayed representing each selected base model's representative token usage with range whiskers

#### Scenario: Bars sorted by representative token count
- **WHEN** model groups have representative effort token totals [5000, 12000, 8000, 3000, 15000]
- **THEN** bars appear from left to right in ascending order: 3000, 5000, 8000, 12000, 15000

#### Scenario: Effort range shown with whisker
- **WHEN** `openai/gpt-5` has effort token totals 5,000, 8,000, and 12,000
- **THEN** the `openai/gpt-5` solid bar extends from 0 to 8,000 and its range whisker spans 5,000-12,000

#### Scenario: Duplicate effort token totals are deduped before selecting representative total
- **WHEN** `openai/gpt-5` has effort token totals 5,000, 5,000, 5,000, 8,000, and 12,000
- **THEN** the `openai/gpt-5` representative token total is 8,000 from deduped values [5,000, 8,000, 12,000]

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

### Requirement: TokenUsageChart is placed on Models overview page

The `TokenUsageChart` component SHALL be rendered on `/` (the Overview/Home page) after the Cost per Full Run section, inside a section labeled "Token Usage". It SHALL be loaded with `client:load`.

#### Scenario: Chart on overview page
- **WHEN** navigating to `/`
- **THEN** a "Token Usage" section with the grouped vertical range-whisker bar chart is visible below the Runtime section

## REMOVED Requirements

### Requirement: TokenUsageChart renders horizontal bar chart
**Reason**: Replaced by the shared vertical representative-bar plus range-whisker chart language.
**Migration**: Use `TokenUsageChart renders vertical range-whisker bar chart`.
