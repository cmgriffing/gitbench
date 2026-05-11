## 1. Python JSON Export

- [x] 1.1 Add `render_json(data, output_path)` function to `gitbench/render.py` that writes full aggregated data as JSON
- [x] 1.2 Extend `aggregate_runs()` output to include fixture-level `prompt`, `expected`, `description`, `purpose`, `difficulty`, `tags`
- [x] 1.3 Extend `aggregate_runs()` to include `baseModel` and `reasoningLevel` per model entry (parse via existing `parse_model_name`)
- [x] 1.4 Ensure full model outputs are included (remove the `[:200]` truncation in aggregate)
- [x] 1.5 Add `--format json` option to `gitbench render` CLI command in `cli.py`
- [x] 1.6 Add `gitbench report` CLI command that chains: aggregate → write JSON → build → optionally open
- [x] 1.7 Add `gitbench report --no-build` flag to skip the npm build step
- [ ] 1.8 Write tests for `render_json()` and new aggregation fields

## 2. Astro Project Scaffolding

- [x] 2.1 Initialize Astro project in `gitbench/ui/` with `npm create astro@latest` (empty template, TypeScript)
- [x] 2.2 Add React integration: `npx astro add react` and install `@astrojs/react`, `react`, `react-dom`, `@types/react`
- [x] 2.3 Install Recharts: `npm install recharts`
- [x] 2.4 Configure `astro.config.mjs` with `@astrojs/react()` integration and `output: 'static'`
- [x] 2.5 Create TypeScript types in `src/lib/types.ts` matching the JSON schema
- [x] 2.6 Create data loader in `src/lib/load-data.ts` that fetches and parses `/results.json`
- [x] 2.7 Add `ui/public/results.json` and `ui/dist/` to `.gitignore`

## 3. Layout, Sidebar, and Styles

- [x] 3.1 Create `src/styles/global.css` with CSS custom properties (dark theme matching current report)
- [x] 3.2 Create `src/components/Layout.astro` with header, sidebar slot, `<slot />` for content, and footer
- [x] 3.3 Create `src/components/Sidebar.astro` with six nav links, active-route highlighting
- [x] 3.4 Add base typography styles (Manrope for display, DM Mono for code/data)

## 4. React Island Components

- [x] 4.1 Create `ModelSelector` React component with multi-select checkboxes, `onChange` callback, `initialSelected` prop, "Select all" / "Clear all" controls
- [x] 4.2 Create `PassRateBarChart` React component using Recharts horizontal bar chart, color-coded by pass rate threshold
- [x] 4.3 Create `BenchmarkHeatmap` React component with benchmark rows × model columns, clickable row labels (→ benchmark page) and column headers (→ model page)
- [x] 4.4 Create `TimeSeriesChart` React component using Recharts line chart with date X-axis and pass rate Y-axis
- [x] 4.5 Create `ScatterPlot` React component for pairwise model similarity comparison with color-coded dots

## 5. Dashboard Page

- [x] 5.1 Create `src/pages/index.astro` rendering summary cards per model (static Astro, linked to model detail)
- [x] 5.2 Add `PassRateBarChart` React island with shared `ModelSelector`
- [x] 5.3 Add `PassByDifficultyChart` React island (optional, or integrate into bar chart)
- [x] 5.4 Add `BenchmarkHeatmap` React island with shared `ModelSelector`

## 6. Model Detail Page

- [x] 6.1 Create `src/pages/models/[model].astro` with `getStaticPaths()` enumerating all model names from results.json
- [x] 6.2 Render model stats section (name, profile, pass rate, similarity, run count) as static Astro
- [x] 6.3 Render fixture gallery as static Astro cards (`FixtureCard.astro`) — one card per fixture result
- [x] 6.4 Create `FilterBar` React island for client-side filtering of fixture cards by benchmark, difficulty, tags
- [x] 6.5 Add reasoning level comparison section (rendered when multiple levels exist for the base model)
- [x] 6.6 Add "Compare →" button that navigates to `/compare?with=<encoded-model-name>`
- [x] 6.7 Add `PassRateBarChart` React island for per-benchmark view (optional, scoped to this model)

## 7. Benchmark Detail Page

- [x] 7.1 Create `src/pages/benchmarks/[name].astro` with `getStaticPaths()` enumerating all benchmark names
- [x] 7.2 Render benchmark description and metadata as static Astro
- [x] 7.3 Render per-fixture comparison table as static Astro (all model results for each fixture in this benchmark)
- [x] 7.4 Add `PassRateBarChart` React island for model leaderboard with `ModelSelector`
- [x] 7.5 Add tag breakdown section (static or chart)

## 8. Fixture Detail Page

- [x] 8.1 Create `src/pages/fixtures/[fixture].astro` with `getStaticPaths()` enumerating all fixture IDs
- [x] 8.2 Create `PromptBlock.astro` component rendering full prompt in monospace with copy button
- [x] 8.3 Create `ExpectedBlock.astro` component rendering full expected text in monospace with copy button
- [x] 8.4 Render fixture metadata (id, description, purpose, difficulty, tags) as static Astro
- [x] 8.5 Create `ModelOutputCard.astro` component for each model's output (model name, pass/fail badge, similarity, full output)
- [x] 8.6 Render all model output cards as static Astro
- [x] 8.7 Add copy-to-clipboard functionality for prompt, expected, and output blocks (vanilla JS or web component)

## 9. Explore Page

- [x] 9.1 Create `src/pages/explore.astro` with tag cloud rendered as static Astro
- [x] 9.2 Create React `FilterBar` island for multi-select tag + difficulty + benchmark filtering
- [x] 9.3 Create React `FilteredResults` island showing matching fixtures with per-model sparkline bars
- [x] 9.4 Add `ModelSelector` React island to the filtered results view

## 10. Compare Page

- [x] 10.1 Create `src/pages/compare.astro` with the ComparePage React island as the primary content
- [x] 10.2 Build multi-select model picker at top of Compare page
- [x] 10.3 Build overall pass rate comparison bar chart
- [x] 10.4 Build per-benchmark grouped comparison chart
- [x] 10.5 Build head-to-head scatter plot (pick 2 models from selected set)
- [x] 10.6 Build agreement matrix (2×2 grid for the 2 selected models)
- [x] 10.7 Build per-fixture detail table (all selected models as columns)
- [x] 10.8 Handle `?with=` query parameter for pre-selection on navigation from Model Detail

## 11. History Page

- [x] 11.1 Create `src/pages/history.astro` with static run log table (timestamp, model, pass rate, suite, delta)
- [x] 11.2 Add `TimeSeriesChart` React island with `ModelSelector`
- [x] 11.3 Implement expandable run rows showing fixture-level regressions and improvements
- [x] 11.4 Compute delta from previous run of the same model+level combination

## 12. Integration and Polish

- [x] 12.1 Verify `gitbench report` end-to-end: run → aggregate → build → open
- [x] 12.2 Verify all static routes are generated correctly (no 404s)
- [ ] 12.3 Test with real multi-model results data from `gitbench-results/`
- [x] 12.4 Ensure responsive layout works on mobile widths
- [x] 12.5 Single rendering path: `gitbench report` only, old render command and HTML generation removed
- [ ] 12.6 Update `CONTRIBUTING.md` with UI development instructions
- [ ] 12.7 Update `README.md` with new report workflow (`gitbench report`)
