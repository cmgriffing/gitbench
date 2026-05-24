## 1. Add per-benchmark pass rate metric

- [x] 1.1 Add `benchPassRateMetric(effort, data, benchName)` to `model-groups.ts` that reads `data.matrix[effort.modelName][benchName].pass_at_k` and returns `MetricEffort | null`

## 2. Fix PassRateBarChart to support per-benchmark filtering

- [x] 2.1 Add optional `benchmarkName?: string` prop to `PassRateBarChart`
- [x] 2.2 When `benchmarkName` is provided, use `benchPassRateMetric` instead of `passRateMetric` in `buildGroupedMetricRows`
- [x] 2.3 Update tooltip footnote to show benchmark-specific fixture count when filtered (e.g., "% of 12 fixtures passed")
- [x] 2.4 Pass `benchmarkName={benchName}` from `benchmarks/[name].astro` to `<PassRateBarChart>`

## 3. Create FixtureComparisonTable React component

- [x] 3.1 Create `gitbench/web/src/components/charts/FixtureComparisonTable.tsx` as a `client:load` React island
- [x] 3.2 Accept `benchmarkName: string` prop
- [x] 3.3 Load data via `loadData()` and derive model groups
- [x] 3.4 Use `useSyncedModelSelection(data)` to get selected groups and `setSelectedGroups`
- [x] 3.5 Render a `ModelSelector` above the table with `value={selectedGroups}` and `onChange={setSelectedGroups}`
- [x] 3.6 Expand selected groups to individual model names via `expandGroupSelection()`
- [x] 3.7 Filter `fixture_index` entries to the given benchmark
- [x] 3.8 Render grouped column headers: parent `<th>` with `colspan` for the model group, child `<th>` for each reasoning effort
- [x] 3.9 Look up results using `data.fixtures[modelName]?.[benchmarkName]` and match by `fixture_index[key].id`
- [x] 3.10 Render cells with similarity percentage in pass/fail colored badges; show "—" for missing results

## 4. Update benchmark detail page

- [x] 4.1 Replace the inline `<table>` section in `benchmarks/[name].astro` with `<FixtureComparisonTable client:load benchName={benchName} />`
- [x] 4.2 Remove the inline fixture iteration and model column rendering from the Astro template (no longer needed server-side)

## 5. Verify

- [x] 5.1 Run `npm run build` in `gitbench/web/` and confirm no build errors
- [x] 5.2 Navigate to `/benchmarks/blame_forensics` and verify table shows similarity percentages instead of "—"
- [x] 5.3 Verify the PassRateBarChart shows per-benchmark pass rates (not global 75%)
- [x] 5.4 Change model selection in the table's ModelSelector and verify the chart updates
- [x] 5.5 Navigate to `/compare`, change model selection, return to benchmark detail, verify selection persisted
