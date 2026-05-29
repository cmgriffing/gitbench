## Why

The benchmark detail page (`/benchmarks/[name]`) is broken in two ways and missing a key feature. The per-fixture comparison table shows "—" in every model column because fixture IDs don't match between `fixture_index` keys and result records. The "Model Leaderboard" chart contradicts its own blurb — it shows global pass rates across all 204 fixtures instead of the pass rate for this benchmark's 12 fixtures. And the table renders all 117 models as columns with no way to filter, unlike every other chart on the site which shares a synced model selection.

## What Changes

- Fix fixture ID mismatch: use `fi.id` instead of `fid` in the table's `results.find()` call
- Fix PassRateBarChart to accept an optional `benchmarkName` prop; when provided, use per-benchmark pass rates from `matrix[model][benchmark]` instead of global `model_summaries`
- Extract the per-fixture comparison table into a React client component (`FixtureComparisonTable.tsx`) with its own `ModelSelector` using the existing synced selection system (localStorage + CustomEvent)
- Add `benchPassRateMetric` to `model-groups.ts` for per-benchmark pass rate extraction
- When selection changes via the table's selector, it syncs across all other selectors on the site

## Capabilities

### New Capabilities
- `fixture-comparison-table`: React client component rendering a per-fixture comparison table with a synced ModelSelector. Each selected model group expands to show individual reasoning effort levels as sub-columns. Only fixture results for the current benchmark are shown.

### Modified Capabilities
- `chart-components`: PassRateBarChart gains an optional `benchmarkName` prop. When provided, the chart computes pass rates from `matrix[model][benchmarkName].pass_at_k` instead of `model_summaries[model].pass_at_k`. When absent, behavior is unchanged (global pass rates).
- `report-pages`: Benchmark Detail page now passes `benchmarkName` to PassRateBarChart and replaces the inline Astro table with the `FixtureComparisonTable` React island. The page no longer renders all 117 models unconditionally; instead the table uses the shared model selection.

## Impact

- `gitbench/web/src/pages/benchmarks/[name].astro` — pass `benchmarkName` to PassRateBarChart, replace inline table with `<FixtureComparisonTable client:load />`
- `gitbench/web/src/components/charts/PassRateBarChart.tsx` — accept optional `benchmarkName` prop, choose metric source
- `gitbench/web/src/components/charts/model-groups.ts` — add `benchPassRateMetric` function
- NEW `gitbench/web/src/components/charts/FixtureComparisonTable.tsx` — React component with ModelSelector + per-effort fixture table
