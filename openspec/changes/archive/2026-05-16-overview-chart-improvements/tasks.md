## 1. CostValueChart rewrite

- [x] 1.1 Replace ScatterChart with a horizontal Recharts BarChart in `CostValueChart.tsx`
- [x] 1.2 Compute chart data from `model_summaries[].total_cost_usd`, exclude null-cost models, sort by cost
- [x] 1.3 Integrate ModelSelector filter (default: all models with cost data), wired to chart data filtering
- [x] 1.4 Render bars with `getProviderColor()`, Y-axis labels with ProviderIcon + truncated name + reasoning level, 350px fixed height, and provider legend below
- [x] 1.5 Implement tooltips showing full model name, cost in USD, and pass rate percentage
- [x] 1.6 Wire bar click to navigate via `modelLevelPath()`
- [x] 1.7 Handle empty/null cost data edge cases (all-null → "No pricing data available")

## 2. TokenUsageChart creation

- [x] 2.1 Create `TokenUsageChart.tsx` with horizontal Recharts BarChart layout
- [x] 2.2 Compute total tokens per model by summing `fixtures[model][].total_tokens` across all runs (null → treat as 0)
- [x] 2.3 Integrate ModelSelector filter (default: all models), wired to chart data filtering
- [x] 2.4 Render bars with `getProviderColor()`, Y-axis labels with ProviderIcon + truncated name + reasoning level, 350px fixed height, and provider legend below
- [x] 2.5 Implement tooltips showing full model name, total tokens (formatted as K/M), and input/output breakdown when available
- [x] 2.6 Handle all-null token data edge case (all-null → "No token data available")
- [x] 2.7 Add token number formatting utility (`12.5K`, `1.2M`)

## 3. Overview page integration

- [x] 3.1 Add `TokenUsageChart` import and section to `index.astro` (labeled "Token Usage", after Cost vs Quality)
- [x] 3.2 Verify all three sections (Model Summary, Benchmark Matrix, Cost vs Quality, Token Usage) render correctly together
