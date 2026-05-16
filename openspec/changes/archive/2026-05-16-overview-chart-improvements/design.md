## Context

The overview page (`index.astro`) currently has three chart sections: PassRateBarChart, BenchmarkHeatmap, and CostValueChart. The CostValueChart uses a Recharts ScatterChart with median reference lines to plot models on a cost vs pass-rate quadrant. Users find this hard to read — dots overlap, exact values are hidden, and the quadrants offer weak signal.

Additionally, there is no token usage visualization anywhere. The data already carries `total_tokens`, `input_tokens`, and `output_tokens` on `FixtureResult`, and `ModelSummary` aggregates costs — but there is no aggregate token column. We will compute total tokens per model client-side by summing fixture-level data.

The existing `PassRateBarChart` establishes a strong visual pattern: horizontal bar chart with provider-colored bars, diagonal model labels with icons, a ModelSelector filter, tooltips, and a provider legend. Both new charts will lean on this pattern for consistency.

## Goals / Non-Goals

**Goals:**
- Replace the CostValueChart quadrant scatter with a horizontal bar chart ranking models by `total_cost_usd`
- Add a new TokenUsageChart bar chart ranking models by total token consumption
- Reuse the existing ModelSelector component so both new charts share a filter
- Match the visual style of PassRateBarChart (bar direction, colors, labels, legend)
- Zero backend/pipeline changes — all new display logic is client-side

**Non-Goals:**
- Changing the PassRateBarChart or BenchmarkHeatmap
- Adding per-fixture token breakdowns (out of scope — just aggregate rankings)
- Supporting arbitrary unit selection (always total tokens, always USD)
- Server-side rendering of charts (they remain `client:load`)

## Decisions

### Decision 1: Horizontal bar charts (not vertical)

**Choice:** Horizontal bars (Y-axis = model, X-axis = metric value).

**Rationale:** The PassRateBarChart uses vertical bars (X-axis = model) with rotated labels, which works for pass rates but gets cramped with longer cost/token labels. Horizontal bars let labels sit cleanly beside each bar with full model names, no rotation needed. They also naturally convey "ranking" — longest bar at top/bottom.

**Alternative considered:** Match PassRateBarChart exactly (vertical bars with -40° rotated labels). Rejected because cost and token axes values have variable magnitude (0.001 to 50.00) that makes bar heights harder to compare than bar widths in a horizontal layout.

### Decision 2: Shared ModelSelector per chart section

**Choice:** Each chart gets its own ModelSelector, not a single global one.

**Rationale:** Users may want to filter differently per chart (e.g., see only cheap models in the cost chart while keeping all models in the token chart). A global filter would force a single view. The existing PassRateBarChart already has its own selector — we follow that pattern.

### Decision 3: Client-side token aggregation

**Choice:** Compute total tokens per model in the TokenUsageChart component by summing `fixtures[modelName]` → each fixture's `total_tokens` values.

**Rationale:** `ModelSummary` has `total_cost_usd` but no `total_tokens`. Adding a pipeline computed field would require re-running all benchmarks. Client-side aggregation from `fixtures` data is fast (sum over ~200 fixtures per model × ~30 models = ~6000 operations, trivial in JS) and avoids a breaking data format change.

**Alternative considered:** Add `total_tokens` to ModelSummary in the Python pipeline. Rejected because it requires re-running benchmarks and modifying the aggregation code, which is high cost for marginal benefit.

### Decision 4: Extract shared bar chart primitives

**Choice:** Do NOT extract a shared bar chart abstraction in this change.

**Rationale:** The three bar charts (PassRateBarChart, CostValueChart, TokenUsageChart) share visual style but differ in data sources, computed values, and rendering details (horizontal vs vertical). Extracting a generic bar chart component would add abstraction complexity without immediate payoff — it's better to keep them as three concrete components and refactor to a shared base only when a fourth chart emerges or duplication becomes painful.

## Risks / Trade-offs

- **Risk:** TokenUsageChart becomes slow with very large datasets (100+ models × 500 fixtures each) → **Mitigation:** For typical datasets (~30 models), the computation is trivial. If it ever becomes slow, memoize with `useMemo`.
- **Risk:** `total_tokens` may be `null` for fixtures where token data wasn't collected → **Mitigation:** Skip null values in the sum. Models with all-null token data show a "No token data available" message (same pattern as cost chart).
- **Risk:** Horizontal bar charts with many models (>40) may create excessive vertical scrolling → **Mitigation:** This is already a problem for PassRateBarChart's 350px fixed height. We'll use the same fixed height. If it becomes an issue, it should be solved holistically, not per-chart.
