## Why

When the output-mode toggle is set to `Both`, charts do not present text and JSON-schema results consistently. Metric bar charts combine modes or render them as unrelated variants, while the quadrant chart collapses both modes to one winning point per base model; these behaviors hide the direct mode comparison.

## What Changes

- Render text and JSON-schema results as adjacent bars within one provider/base-model category when `Both` is selected.
- Compute the representative value and effort range independently for each output mode.
- Apply paired output-mode bars to every current bar chart: overview pass rate, benchmark leaderboard pass rate, cost, API time, token usage, Compare overall pass rate, and Compare per-benchmark pass rate.
- Keep paired bars visually grouped through a shared category or model-effort identity, compact intra-pair spacing, the chart's existing base color semantics, and a mode-style legend.
- Use one category-level tooltip for either sibling bar, with separate `Text` and `JSON` effort lists and independent representative markers.
- For Compare's per-benchmark chart, resolve either hovered mode series to one model-effort pair so its tooltip shows only that pair's `Text` and `JSON` values for the benchmark.
- Preserve one-bar rendering for `Text`-only and `JSON`-only selections.
- Leave a missing mode's bar slot empty when a selected model group has data for only one mode, while making the missing state clear in the shared tooltip.
- Sort model categories deterministically in `Both` mode using the mean of the available mode representative values; use the available value directly when only one mode exists.
- Consolidate Compare chart labels and legends around canonical model-effort identities instead of exposing `__json_schema` variants as unrelated models.
- Render separate text and JSON points for each selected base model in the quadrant chart when `Both` is selected, choosing the best available effort independently within each mode.
- Connect paired quadrant points with a subtle line, use the shared solid-text and translucent-outlined-JSON treatments, and keep coincident points individually visible.
- Use one paired quadrant tooltip from either point with separate mode metrics, reasoning efforts, and an explicit missing-mode state.
- Make quadrant ranking and "Best blend" mode-specific so a text point and a JSON point can rank independently.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `chart-components`: Change shared grouped metric rows, paired-bar rendering, mode styling, shared tooltip behavior, `Both`-mode sorting, and quadrant point expansion.
- `runtime-chart`: Show independent text and JSON-schema API-time bars, ranges, and tooltip sections.
- `cost-value-chart`: Show independent text and JSON-schema cost bars, ranges, and tooltip sections.
- `token-usage-chart`: Show independent text and JSON-schema token bars, ranges, and tooltip sections.
- `report-pages`: Apply paired output-mode bars and pair-level tooltips to both Compare page bar charts.

## Impact

- Web chart data shaping in `gitbench/web/src/components/charts/model-groups.ts`.
- Shared Recharts rendering and legends in `gitbench/web/src/components/charts/grouped-chart-ui.tsx`.
- Tooltip content and sorting in `PassRateBarChart`, `RuntimeBarChart`, `CostValueChart`, and `TokenUsageChart`.
- Compare page bar data shaping, rendering, legends, and tooltips in `gitbench/web/src/components/ComparePage.tsx`.
- Quadrant point selection, rendering, connectors, ranking, and tooltips in `gitbench/web/src/components/charts/QuadrantComparisonChart.tsx`.
- Focused tests or extracted helper tests for per-mode aggregation, model-variant pairing, quadrant point selection, missing-mode behavior, and sorting.
- No report API, database, route, or dependency changes are expected.
