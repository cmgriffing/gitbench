## Purpose

The RuntimeBarChart provides a bar chart ranking models by total wall-clock runtime, fastest first.
## Requirements
### Requirement: RuntimeBarChart renders horizontal bar chart ranking models by speed
The `RuntimeBarChart` React component SHALL render a Recharts horizontal bar chart (bars go right, Y-axis = model, X-axis = total runtime in seconds). Each bar SHALL represent one model's total wall-clock time aggregated across all fixtures from `model_runtimes[model].total_ms`. Bars SHALL be color-coded by provider using the `getProviderColor()` palette. Y-axis tick labels SHALL display the provider brand icon (via `ProviderIcon`), the truncated model name (max ~10 characters + ellipsis), and the reasoning level suffix. The component SHALL accept a `data` prop containing the full dataset and an optional `selectedModels` prop for filtering. Chart height SHALL be fixed at 350 pixels. A provider legend SHALL be rendered below the chart card showing colored dots for each unique provider present. Models SHALL be sorted fastest-first (ascending total runtime).

#### Scenario: Bars render for selected models
- **WHEN** `RuntimeBarChart` receives `selectedModels=['anthropic/claude-opus-4.7:low', 'openai/gpt-oss-120b:high']`
- **THEN** two horizontal bars are displayed with the corresponding total runtimes

#### Scenario: Fastest model appears at top
- **WHEN** models have total runtimes [5000, 12000, 3000, 8000]
- **THEN** bars appear in order: 3000 (top), 5000, 8000, 12000 (bottom)

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

### Requirement: RuntimeBarChart reads from model_runtimes in aggregated data
The `RuntimeBarChart` component SHALL read runtime data from `data.model_runtimes[modelName].total_ms`. It SHALL convert milliseconds to seconds for display (dividing by 1000). The X-axis SHALL be labeled in seconds (e.g., "120s", "45.3s").

#### Scenario: Total runtime converted to seconds
- **WHEN** a model has `total_ms=45300`
- **THEN** the bar represents 45.3 seconds and the X-axis tick shows "45.3s"

#### Scenario: Zero millisecond total handled
- **WHEN** a model has `total_ms=0`
- **THEN** the bar represents 0 seconds and the X-axis tick shows "0s"

### Requirement: RuntimeBarChart shows tooltips on hover
Hovering over a bar SHALL display a tooltip with the full model name, total runtime in seconds and minutes, and average per-fixture time in seconds (from `model_runtimes[model].avg_ms`).

#### Scenario: Tooltip on hover
- **WHEN** a user hovers over a model bar
- **THEN** a tooltip appears showing the full model name and total runtime (e.g., "1m 23s (83.0s)")

#### Scenario: Tooltip shows average per-fixture time
- **WHEN** a user hovers over a model bar
- **THEN** the tooltip shows average fixture time (e.g., "Avg: 2.5s per fixture")

### Requirement: RuntimeBarChart handles models without runtime data
If a selected model has no entry in `model_runtimes` (no timing data available), it SHALL be excluded from the chart. If NO selected model has runtime data, the component SHALL display a message: "No runtime data available."

#### Scenario: Model without runtime data excluded
- **WHEN** one model is selected but has no `model_runtimes` entry
- **THEN** that model does not appear as a bar

#### Scenario: All models lack runtime data
- **WHEN** every selected model has no `model_runtimes` entry
- **THEN** the chart area displays "No runtime data available"

### Requirement: RuntimeBarChart includes ModelSelector filter
The `RuntimeBarChart` component SHALL include a `ModelSelector` dropdown allowing users to filter which models appear in the chart. The selector SHALL default to all models that have runtime data selected.

#### Scenario: Filter removes models from chart
- **WHEN** a user deselects a model in the ModelSelector
- **THEN** that model's bar is removed from the chart

### Requirement: RuntimeBarChart is placed on Models overview page
The `RuntimeBarChart` component SHALL be rendered on `/` (the Overview/Home page) after the Cost per Full Run section, in its own section labeled "Runtime (Wall Clock)". It SHALL be loaded with `client:load`.

#### Scenario: Chart on overview page
- **WHEN** navigating to `/`
- **THEN** a "Runtime (Wall Clock)" section with the horizontal bar chart is visible
