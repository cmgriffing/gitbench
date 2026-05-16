## Why

The quadrant scatter plot on the overview page (CostValueChart) is a weak visualization for comparing model costs — it crowds dots into overlapping clusters, makes exact values hard to read, and the median reference lines offer little actionable insight. Additionally, there is no way to compare token consumption across models, which is a key differentiator for cost-aware model selection. Bar charts provide instant rank-order clarity for both pricing and token metrics.

## What Changes

- Replace the `CostValueChart` quadrant scatter plot with a **horizontal bar chart** that ranks models by total cost per full run (lowest → highest), reusing the existing bar chart patterns from `PassRateBarChart`
- Add a new **token usage ranking chart** section on the overview page that shows total tokens consumed per full run for each model, ranked lowest to highest
- Both charts share the same ModelSelector filter, provider color coding, and provider legend patterns already established by `PassRateBarChart`

## Capabilities

### New Capabilities
- `token-usage-chart`: A horizontal bar chart ranking models by total token consumption across all runs, with provider color coding, model name labels, tooltips, and provider legend. Placed as a new section on the overview page.

### Modified Capabilities
- `cost-value-chart`: Replace the quadrant scatter plot with a horizontal bar chart ranking models by total cost per full run. The chart SHALL still use `total_cost_usd` from model summaries. Bar-based rendering replaces scatter plot — dots, reference lines, and ZAxis are removed. All existing behavior around missing cost data and loading states is preserved.

## Impact

- **Affected code**: `CostValueChart.tsx` (complete rewrite), `index.astro` (add new section + update existing one)
- **New code**: `TokenUsageChart.tsx` (new chart component)
- **No API or data changes**: Both charts consume existing fields (`total_cost_usd`, `total_tokens`) from `ModelSummary` and `FixtureResult` — no backend or pipeline changes needed
