## Why

GitBench currently generates a single scrollable HTML page with embedded Chart.js. Results now carry rich metadata — fixture purposes, difficulty levels, tags, per-model reasoning levels, token usage, run history — but the report doesn't expose this depth. A multi-page, browsable static web application makes the data explorable: click a model to see its fixture gallery, click a tag to cross-reference benchmarks, compare models head-to-head, track pass rates over time.

## What Changes

- Replace the single-page Python-generated HTML report with an Astro SSG site at `gitbench/web/`
- Astro renders layout, text, tables, and fixture cards as static HTML at build time
- React islands handle interactive elements only: charts (bar, heatmap, scatter, time series) and model selection
- Multi-select model picker treats models and reasoning levels as independently selectable (e.g., `gpt-4o#high`, `gpt-4o#low`, and `claude-sonnet` in any combination)
- Seven routes: Dashboard, Model Detail, Benchmark Detail, Fixture Detail, Explore, Compare, History
- Dedicated `/compare` route for multi-model analysis with scatter plots, agreement matrix, and per-fixture detail
- Model Detail page includes a "Compare →" button that navigates to `/compare` with that model pre-selected
- Fixture Detail page shows full prompt text, expected text, and all model outputs side by side
- Explore page provides tag-cloud navigation and cross-benchmark fixture search by tag + difficulty
- History page shows pass rate time series and run log with per-fixture regression/improvement deltas
- Python side gains `render_json()` export and `gitbench report` CLI command (the single rendering path)
- The old `render_html()` single-page report is removed from the CLI

## Capabilities

### New Capabilities

- `astro-site`: Astro project scaffolding, build pipeline, static Layout and Sidebar components, CSS design tokens, client-side routing
- `report-pages`: All seven page routes (Dashboard, Model Detail, Benchmark Detail, Fixture Detail, Explore, Compare, History) with their static content and React island placements
- `chart-components`: React island components — ModelSelector (multi-select), PassRateBarChart, BenchmarkHeatmap, TimeSeriesChart, ScatterPlot
- `json-export`: Python-side `render_json()` function and `gitbench report` CLI command (the sole rendering path)

### Modified Capabilities

<!-- None -->

## Impact

- **New**: `gitbench/web/` — Astro project (package.json, astro.config.mjs, src/pages/, src/components/, src/lib/, src/styles/, public/)
- **Modified**: `gitbench/render.py` — add `render_json()` and enrich `aggregate_runs()` output
- **Modified**: `gitbench/cli.py` — replace `render` command with `report` command; remove HTML generation from `run`
- **Modified**: `gitbench/harness/types.py` — add `prompt`, `expected`, `description` to `Score`
- **Modified**: `gitbench/harness/runner.py` — populate `prompt`/`expected`/`description` on scores
- **Dependencies**: Node.js, npm, Astro, React 19, Recharts, @astrojs/react
- **Build pipeline**: Python CLI generates `web/public/results.json`, then `npm run build` produces static `web/dist/`
