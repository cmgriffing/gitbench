## Purpose

The CostValueChart provides a quadrant scatter plot comparing each model's total cost against its pass rate.
## Requirements
### Requirement: CostValueChart shows tooltips on hover

Hovering over a bar SHALL display a tooltip with the full model name, total cost formatted as USD (e.g., "$0.5270" or "$12.50"), and pass rate percentage for context.

#### Scenario: Tooltip on hover
- **WHEN** a user hovers over a model bar
- **THEN** a tooltip appears showing the full model name, total cost in USD format, and pass rate percentage

### Requirement: CostValueChart handles models without cost data

Models with no cost data (`total_cost_usd` is null) SHALL NOT appear on the chart. If ALL models lack cost data, the component SHALL display a message: "No pricing data available."

#### Scenario: Model without cost is excluded
- **WHEN** one model has null `total_cost_usd` and others have valid costs
- **THEN** only the models with valid costs appear as bars

#### Scenario: All models lack cost data
- **WHEN** every model has null `total_cost_usd`
- **THEN** the chart area displays "No pricing data available"

### Requirement: CostValueChart is placed on Models overview page

The `CostValueChart` component SHALL be rendered on `/` (the Overview/Home page) inside a section labeled "Cost vs Quality". It SHALL be loaded with `client:load`.

#### Scenario: Chart on overview page
- **WHEN** navigating to `/`
- **THEN** a "Cost vs Quality" section with the horizontal bar chart is visible below the benchmark heatmap

### Requirement: CostValueChart renders horizontal bar chart

The `CostValueChart` React component SHALL render a Recharts horizontal bar chart (bars go right, Y-axis = model, X-axis = total cost in USD). Each bar SHALL represent one model's total cost for a full run using `summary.total_cost_usd` from model summaries. Bars SHALL be color-coded by provider using the `getProviderColor()` palette. Y-axis tick labels SHALL display the provider brand icon (via `ProviderIcon`), the truncated model name (max ~10 characters + ellipsis), and the reasoning level suffix. The component SHALL accept a `data` prop containing the full dataset. Chart height SHALL be fixed at 350 pixels. A provider legend SHALL be rendered below the chart card showing colored dots for each unique provider present.

#### Scenario: One bar per model
- **WHEN** `CostValueChart` renders with 5 models
- **THEN** 5 horizontal bars appear representing each model's total cost

#### Scenario: Bars sorted by cost
- **WHEN** model costs are [0.10, 0.20, 0.50, 0.80, 1.00]
- **THEN** bars appear in ascending order from lowest cost to highest (or descending)

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

### Requirement: CostValueChart bars navigate to model detail

Clicking a bar SHALL navigate the browser to `/models/<provider>/<base-model>/<level>/`.

#### Scenario: Click navigates to model detail
- **WHEN** a user clicks on the bar for model "anthropic/claude-opus-4.7:low"
- **THEN** the browser navigates to `/models/anthropic/claude-opus-4.7/low/`

### Requirement: CostValueChart includes ModelSelector filter

The `CostValueChart` component SHALL include a `ModelSelector` dropdown allowing users to filter which models appear in the chart. The selector SHALL default to all models selected.

#### Scenario: Filter removes models from chart
- **WHEN** a user deselects a model in the ModelSelector
- **THEN** that model's bar is removed from the chart

