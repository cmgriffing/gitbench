# token-usage-chart Specification

## Purpose
TBD - created by archiving change overview-chart-improvements. Update Purpose after archive.
## Requirements
### Requirement: TokenUsageChart renders horizontal bar chart

The `TokenUsageChart` React component SHALL render a Recharts horizontal bar chart (bars go right, Y-axis = model, X-axis = total tokens). Each bar SHALL represent one model's total token consumption summed across all fixtures. Bars SHALL be color-coded by provider using the `getProviderColor()` palette. Y-axis tick labels SHALL display the provider brand icon (via `ProviderIcon`), the truncated model name (max ~10 characters + ellipsis), and the reasoning level suffix. The component SHALL accept a `data` prop containing the full dataset. Chart height SHALL be fixed at 350 pixels. A provider legend SHALL be rendered below the chart card showing colored dots for each unique provider present.

#### Scenario: Bars render for all models
- **WHEN** `TokenUsageChart` renders with 5 models
- **THEN** 5 horizontal bars are displayed representing each model's total token consumption

#### Scenario: Bars sorted by token count
- **WHEN** models have total token counts [5000, 12000, 8000, 3000, 15000]
- **THEN** bars appear in ascending order: 3000, 5000, 8000, 12000, 15000 (or descending)

#### Scenario: Colors reflect provider
- **WHEN** a model has provider `anthropic`
- **THEN** its bar is rendered in the Anthropic palette color (#D97757)

#### Scenario: Colors reflect provider for fallback providers
- **WHEN** a model has provider `unknown-provider`
- **THEN** its bar is rendered in a deterministic `hsl(hue, 55%, 48%)` color

#### Scenario: Y-axis labels show provider icon and truncated name
- **WHEN** a model name is `openai/gpt-oss-120b:high`
- **THEN** its Y-axis tick shows the OpenAI icon, "gpt-oss-1…" (truncated), and "high" side-by-side

#### Scenario: Long model names are truncated
- **WHEN** a model name exceeds ~10 characters in the base model part
- **THEN** the displayed label is truncated with an ellipsis

#### Scenario: Chart height is fixed at 350 pixels
- **WHEN** 5, 12, or 30 models are present
- **THEN** the chart height is always 350 pixels

#### Scenario: Provider legend appears below the chart
- **WHEN** the chart shows models from multiple providers
- **THEN** a horizontal legend with colored dots and provider names appears below the chart card

### Requirement: TokenUsageChart computes total tokens from fixture data

The `TokenUsageChart` component SHALL compute total tokens per model by summing `total_tokens` across all fixture results for that model. Null `total_tokens` values SHALL be treated as 0 in the sum. The computed total SHALL be displayed as a formatted number (e.g., "12.5K" for 12,500, "1.2M" for 1,200,000).

#### Scenario: Tokens summed across fixtures
- **WHEN** a model has 3 fixtures with total_tokens [100, 200, null]
- **THEN** the model's bar represents 300 total tokens

#### Scenario: Model with all null token data
- **WHEN** every fixture for a model has `total_tokens: null`
- **THEN** that model shows 0 tokens and appears at the bottom of the ranking

#### Scenario: Large token counts are formatted compactly
- **WHEN** a model has 1,250,000 total tokens
- **THEN** the tooltip and axis display "1.25M"

### Requirement: TokenUsageChart shows tooltips on hover

Hovering over a bar SHALL display a tooltip with the full model name, total tokens formatted compactly, and token breakdown (input + output) when available.

#### Scenario: Tooltip on hover
- **WHEN** a user hovers over a model bar
- **THEN** a tooltip appears showing the full model name and total token count

#### Scenario: Tooltip shows breakdown when available
- **WHEN** input_tokens and output_tokens data exists for the model
- **THEN** the tooltip shows input and output token counts in addition to total

### Requirement: TokenUsageChart handles empty token data

If ALL models have no token data (every `total_tokens` is null), the component SHALL display a message: "No token data available."

#### Scenario: All models lack token data
- **WHEN** every fixture across all models has `total_tokens: null`
- **THEN** the chart area displays "No token data available"

### Requirement: TokenUsageChart is placed on Models overview page

The `TokenUsageChart` component SHALL be rendered on `/` (the Overview/Home page) after the Cost vs Quality section, inside a section labeled "Token Usage". It SHALL be loaded with `client:load`.

#### Scenario: Chart on overview page
- **WHEN** navigating to `/`
- **THEN** a "Token Usage" section with the horizontal bar chart is visible below the Cost vs Quality section

### Requirement: TokenUsageChart includes ModelSelector filter

The `TokenUsageChart` component SHALL include a `ModelSelector` dropdown allowing users to filter which models appear in the chart. The selector SHALL default to all models selected.

#### Scenario: Filter removes models from chart
- **WHEN** a user deselects a model in the ModelSelector
- **THEN** that model's bar is removed from the chart

