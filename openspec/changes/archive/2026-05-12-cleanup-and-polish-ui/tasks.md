## 1. Dead Code Removal

- [x] 1.1 Remove `render_html()` function (lines 322–1127) from `gitbench/render.py`
- [x] 1.2 Remove `render_html_from_envelope()` function from `gitbench/render.py`
- [x] 1.3 Remove `TestRenderHtml` class (5 tests) from `tests/test_render.py`
- [x] 1.4 Remove `TestRenderCommand` class (7 tests) from `tests/test_render.py`
- [x] 1.5 Remove `TestRenderReasoningLevel` class (5 tests) from `tests/test_render.py`
- [x] 1.6 Delete `index.html` from project root
- [x] 1.7 Delete stale report screenshots from project root (`gitbench-*.png`, 5 files)
- [x] 1.8 Verify remaining tests in `test_render.py` still pass (`TestLoadRunsFromDir`, `TestLoadRunsFromJsonl`, `TestAggregateRuns`)

## 2. Tailwind CSS + shadcn/ui Setup

- [x] 2.1 Install Tailwind CSS v4 and `@tailwindcss/vite` in `gitbench/web/`
- [x] 2.2 Create `postcss.config.js` (or verify v4 zero-config works with Astro)
- [x] 2.3 Add `@import "tailwindcss"` directive to `gitbench/web/src/styles/global.css`
- [x] 2.4 Map existing CSS custom properties into Tailwind `@theme` block in `global.css`
- [x] 2.5 Install shadcn/ui dependencies: `class-variance-authority`, `clsx`, `tailwind-merge`
- [x] 2.6 Create `gitbench/web/src/lib/utils.ts` with `cn()` helper
- [x] 2.7 Run `npx shadcn@latest init` with manual config pointing to `src/components/ui/`
- [x] 2.8 Add shadcn components via CLI: `button`, `card`, `badge`, `select`, `command`, `popover`
- [x] 2.9 Verify `npm run build` succeeds with Tailwind + shadcn in place

## 3. shadcn Component Integration

- [x] 3.1 Add `@` path alias to `tsconfig.json` (map `@/*` → `src/*`)
- [x] 3.2 Verify Card, Badge, Button render correctly in a test `.astro` page without `client:*`
- [x] 3.3 Replace `.result-pill`, `.tag-pill`, `.heat-pill` CSS classes with Badge usage across all pages
- [x] 3.4 Replace section-label pattern with Tailwind utility classes
- [x] 3.5 Remove unused CSS classes from `global.css` that are now covered by Tailwind/shadcn

## 4. Lucide Icons (Sidebar)

- [x] 4.1 Install `lucide-react` in `gitbench/web/`
- [x] 4.2 Import the six mapped icon components in `Sidebar.astro`
- [x] 4.3 Use `<LayoutDashboard size={18} strokeWidth={2} />` syntax for each icon (server-side render, no `client:*`)
- [x] 4.4 Verify icons inherit `currentColor` for active/hover states
- [x] 4.5 Verify active/hover color states work correctly on icons
- [x] 4.6 Remove `.sidebar-link .icon` CSS rules (font-size, width) if no longer needed

## 5. Searchable Multi-Select ModelSelector

- [x] 5.1 Rewrite `ModelSelector.tsx` to use `Popover` + `Command` components
- [x] 5.2 Implement trigger button showing selected count or model names
- [x] 5.3 Implement `CommandInput` with search filtering by `model.name` (case-insensitive substring)
- [x] 5.4 Implement `CommandItem` list with checkbox indicators and pass rate display
- [x] 5.5 Implement "Select all" / "Clear all" buttons
- [x] 5.6 Implement `onChange` callback with debounced single-call semantics
- [x] 5.7 Support `initialSelected` prop for pre-selection
- [x] 5.8 Verify integration with all consumers: Dashboard (`index.astro`), Compare (`ComparePage.tsx`), BenchmarkHeatmap, PassRateBarChart, TimeSeriesChart, Explore
- [x] 5.9 Remove old pill-checkbox CSS and unused state from `ModelSelector.tsx`

## 6. Page-Level Inline Style Conversion

- [x] 6.1 Convert `pages/index.astro` (Dashboard) — replace inline styles with Tailwind + Badge/Card
- [x] 6.2 Convert `pages/models/[model].astro` (Model Detail) — filter bar, reasoning levels section, gallery
- [x] 6.3 Convert `pages/models/index.astro` (Models listing)
- [x] 6.4 Convert `pages/benchmarks/[name].astro` (Benchmark Detail) — comparison table, leaderboard
- [x] 6.5 Convert `pages/benchmarks/index.astro` (Benchmarks listing)
- [x] 6.6 Convert `pages/explore.astro` — tag cloud, filter selects, result cards
- [x] 6.7 Convert `pages/history.astro` — run log table, time series chart section
- [x] 6.8 Convert `pages/fixtures/[benchmark]/[fixture].astro` — metadata, output cards
- [x] 6.9 Convert `pages/compare.astro` — wrapper layout adjustments
- [x] 6.10 Convert `components/fixtures/FixtureCard.astro` — use Badge, Tailwind
- [x] 6.11 Convert `components/fixtures/ModelOutputCard.astro`
- [x] 6.12 Convert `components/fixtures/PromptBlock.astro` and `ExpectedBlock.astro`
- [x] 6.13 Convert inline styles in chart components (`ScatterPlot.tsx`, `BenchmarkHeatmap.tsx`, `PassRateBarChart.tsx`, `TimeSeriesChart.tsx`)

## 7. Remaining astro-report-ui Tasks

- [x] 7.1 Write unit tests for `render_json()` function in `tests/test_render.py`
- [x] 7.2 Write tests for new aggregation fields (prompt, expected, description, purpose, difficulty, tags) in `aggregate_runs()`
- [x] 7.3 Test end-to-end with real multi-model results data from `gitbench-results/`
- [x] 7.4 Update `CONTRIBUTING.md` with UI development instructions (Tailwind, shadcn, Astro dev workflow)
- [x] 7.5 Update `README.md` with new report workflow (`gitbench report`)

## 8. Final Integration & Verification

- [x] 8.1 Run `gitbench report` end-to-end: aggregate → build → verify all static routes
- [x] 8.2 Verify all seven routes load without 404s in the built `dist/`
- [x] 8.3 Verify responsive layout on mobile widths (sidebar collapse, card grid)
- [x] 8.4 Verify no console errors in the browser for any page
- [x] 8.5 Run full test suite: `pytest tests/` (Python) and verify Astro build succeeds
- [x] 8.6 Visually verify the searchable multi-select works on Dashboard, Compare, and Explore pages
- [x] 8.7 Visually verify Lucide icons render correctly in sidebar across Chrome and Firefox
