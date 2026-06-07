## 1. Per-Mode Metric Data

- [x] 1.1 Extend grouped metric row types to store independent text and JSON effort lists, representative medians, minimums, maximums, and whisker offsets.
- [x] 1.2 Update `buildGroupedMetricRows()` to partition efforts by output mode before calculating deduped medians and ranges, while preserving groups with only one available mode.
- [x] 1.3 Add a shared sort-value helper that uses the selected mode representative or the mean of available text and JSON representatives in `Both` mode.
- [x] 1.4 Add reusable helpers that pair concrete text and `__json_schema` model variant keys under one canonical model-effort identity for Compare charts.
- [x] 1.5 Add focused Node tests for per-mode aggregation, variant pairing, even-sized medians, duplicate values, missing modes, and `Both`-mode sort values.

## 2. Shared Paired-Bar Rendering

- [x] 2.1 Update `VerticalGroupedMetricChart` to render one mode series for single-mode selections and adjacent text/JSON series for `Both`.
- [x] 2.2 Attach each mode's range whisker to its own bar and scale bar width and intra-category spacing for one or two visible series.
- [x] 2.3 Add reusable output-mode bar styling that renders text with the chart's solid base color and JSON with the same translucent outlined color, without changing click navigation.
- [x] 2.4 Add an output-mode style legend for `Both` while preserving the existing provider legend.
- [x] 2.5 Keep Recharts category-level tooltip activation so either sibling bar resolves to the same provider/base-model row, including keyboard interaction.

## 3. Overview and Benchmark Metric Charts

- [x] 3.1 Update `PassRateBarChart` sorting and tooltip content to show separate Text and JSON sections, per-mode representative medians, effort lists, missing-mode states, and the existing fixture-count footnote.
- [x] 3.2 Update `RuntimeBarChart` sorting and tooltip content to show separate mode medians, effort API times, average fixture API times, missing-mode states, and the existing latency footnote.
- [x] 3.3 Update `CostValueChart` sorting and tooltip content to show separate mode medians, effort costs, pass-rate context, missing-mode states, and the existing cost footnote.
- [x] 3.4 Update `TokenUsageChart` sorting and tooltip content to show separate mode medians, effort totals, input/output breakdowns, missing-mode states, and the existing efficiency footnote.
- [x] 3.5 Verify single-mode selections still render one bar per model category with unchanged ordering and no empty sibling slot.

## 4. Compare Page Bar Charts

- [x] 4.1 Reshape Compare overall pass-rate data into canonical model-effort rows with adjacent text and JSON values, missing-mode support, and mean-representative sorting in `Both`.
- [x] 4.2 Add a shared Text/JSON tooltip to Compare overall so either horizontal sibling bar opens the same model-effort details.
- [x] 4.3 Reshape Compare per-benchmark series so each canonical model effort's text and JSON bars are consecutive and share one model color plus the common mode treatments.
- [x] 4.4 Add item-level pair tooltip resolution to Compare per-benchmark so hovering either sibling shows only that model effort's separate Text and JSON values for the active benchmark.
- [x] 4.5 Consolidate Compare labels and legends around canonical model-effort identities and add the output-mode style legend in `Both`.
- [x] 4.6 Verify Compare single-mode selections retain one bar per model effort and preserve benchmark ordering.

## 5. Quadrant Output-Mode Points

- [x] 5.1 Update quadrant point building to select the highest-composite effort independently for each provider/base-model group and output mode.
- [x] 5.2 Preserve one point per base model in single-mode views and return up to one text point plus one JSON point per base model in `Both`.
- [x] 5.3 Render paired point connectors behind the scatter points and apply solid text and translucent outlined JSON point treatments.
- [x] 5.4 Render coincident text/JSON coordinates as a solid text point plus a larger JSON ring without altering metric coordinates.
- [x] 5.5 Add one paired quadrant tooltip from either point with separate mode metrics, selected reasoning efforts, and `No data` for a missing sibling.
- [x] 5.6 Update the provider/mode legends, "Best blend" label, and top-six ranking so output-mode points are distinguishable and ranked independently.
- [x] 5.7 Add focused tests for independent per-mode selection, differing reasoning efforts, missing siblings, coincident points, tooltip pair lookup, and mode-specific ranking.

## 6. Verification

- [x] 6.1 Run `pnpm test:api` in `gitbench/web` and fix any grouping or report regressions.
- [x] 6.2 Run focused tests covering the shared metric bars, both Compare bar charts, and quadrant point pairing.
- [x] 6.3 Run the configured web formatter on the touched source and test files.
- [x] 6.4 Run `pnpm build` in `gitbench/web` and verify every affected chart compiles with text, JSON, and Both selections.
- [x] 6.5 Browser-smoke the overview, benchmark leaderboard, both Compare bar charts, and quadrant chart in `Both` mode to verify paired geometry, legends, shared tooltips, connectors, and overlap handling.
- [x] 6.6 Run `openspec validate separate-output-mode-chart-variants --strict`.
