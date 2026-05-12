## Context

GitBench currently generates HTML reports via `render.py`, which produces a single static page with embedded Chart.js and inline `<script>` tags. The render function aggregates run envelopes into a structured dict, then builds an HTML string combining CSS, markup, and JavaScript.

The existing data pipeline is:
```
gitbench run → gitbench-results/<timestamp>/*.json (raw envelopes)
gitbench render → index.html (single page)
```

This change introduces a multi-page Astro SSG site that replaces the single-page output as the primary report format. The existing `render_html()` is preserved for backward compatibility.

## Goals / Non-Goals

**Goals:**
- Astro SSG site at `gitbench/ui/` that builds to static HTML/CSS/JS
- Seven routes: Dashboard, Model Detail, Benchmark Detail, Fixture Detail, Explore, Compare, History
- Astro renders layout, text, tables, fixture cards statically at build time
- React islands only for interactive charts and model selection
- Multi-select model picker with independent model+level selection
- Dedicated Compare page with scatter plots, agreement matrix, per-fixture detail
- Python-side JSON export (`render_json()`) that feeds the Astro build
- CLI command `gitbench report` that chains run → aggregate → build → open

**Non-Goals:**
- Server-side rendering or API backend — fully static output
- Text diff view between model output and expected (deferred)
- Auto-generated insight annotations (deferred)
- Replacing the existing `render_html()` — it remains available via `render --format html`
- Live data updates or WebSocket connections

## Decisions

### Decision 1: Astro SSG with React islands

**Rationale:** Astro is purpose-built for content sites where most content is static and only specific components need interactivity. The benchmark report is read-only, data is known at build time, and the only interactivity is chart rendering and model selection. Astro renders the page shell (Layout, Sidebar, tables, text blocks) as zero-JS static HTML, while React islands hydrate only the charts and selectors. This gives the fastest possible page loads with minimal client-side JavaScript.

**Alternatives considered:**
- Pure React SPA — rejected; overkill for a read-only report, worse initial load, unnecessary client-side routing JS
- Next.js SSG — rejected; heavier than Astro, React-first when we want Astro-first
- Keep current single-page Python HTML — rejected; doesn't support multi-page browsing, exploration, or the rich metadata we now have

### Decision 2: results.json in public/ directory, fetched by React islands

**Rationale:** The aggregated dataset (~200 fixtures × N models × full outputs) can be several MB. Embedding it as a prop in every page's Astro frontmatter would duplicate it across all static HTML pages. Instead, `results.json` lives in `ui/public/` as a static asset. React islands fetch it at runtime with browser caching — first page load downloads it, subsequent page navigations read from cache.

**Alternatives considered:**
- Embed full data in each page — rejected; wasteful duplication across 7+ static pages
- Per-page data slicing — rejected; would require complex Python-side slicing, and the full dataset is needed for the Compare and Explore pages anyway
- Astro content collections — rejected; not designed for programmatically-generated JSON

### Decision 3: ModelSelector as separate React island, not embedded in each chart

**Rationale:** Multiple charts on the same page (e.g., Dashboard has PassRateBar, PassByDifficulty, and Heatmap) should share model selection state. By making ModelSelector a standalone component that communicates via React context or lifted state, selecting models in one place updates all charts on the page simultaneously.

**Alternatives considered:**
- Each chart has its own embedded selector — rejected; duplicated UI, inconsistent state across charts
- URL query params for model selection — rejected; adds unnecessary page reloads and doesn't work well with SSG

### Decision 4: Model and reasoning levels are independently multi-selectable

**Rationale:** The user wants "the broadest comparisons possible." Treating `gpt-4o#high` and `gpt-4o#low` as entirely independent entries in a flat multi-select list is simpler to implement and more flexible than a grouped/hierarchical selector. A convenience button ("Select all gpt-4o levels") can be added for quick selection of all reasoning levels for a base model.

**Alternatives considered:**
- Grouped by base model with toggles — rejected; adds complexity without clear benefit given the user's preference for maximum flexibility

### Decision 5: Compare is a dedicated route, not a mode

**Rationale:** The Compare page has fundamentally different layout needs (dense multi-column tables, side-by-side scatter plots, agreement matrices). Making it a dedicated route with its own layout allows optimization for comparison workflows without compromising the focused layouts of model/benchmark/fixture pages. The Model Detail page links to it via a "Compare →" button that passes the current model as a pre-selection.

**Alternatives considered:**
- Compare as a mode toggle on Model Detail — rejected; constrains the UI to fit within model-detail layout, limits comparison features

### Decision 6: Astro renders fixture cards statically, React FilterBar controls visibility

**Rationale:** On the Model Detail page, the fixture gallery contains up to ~200 cards. Rendering them in Astro at build time means zero JS for the core content. A lightweight React FilterBar island adds client-side filtering by toggling CSS `display` on the static cards. This keeps the majority of the page as static HTML.

**Alternatives considered:**
- React renders the entire gallery — rejected; unnecessary client-side rendering of static content
- Build-time filtering with separate routes per filter combination — rejected; explosion of static pages

## Risks / Trade-offs

- **[Risk] Large results.json impacts initial load** → Mitigation: gzip compression (built into most static servers), browser caching across page navigations. For very large datasets (>5MB), consider streaming or pagination in a future iteration.
- **[Risk] Model names with special characters in URLs** → Mitigation: `encodeURIComponent`/`decodeURIComponent` for model names in route params. Astro's `[model].astro` handles this naturally.
- **[Risk] Astro build dependency adds complexity to Python tool** → Mitigation: `gitbench report` is a convenience command. Users can also run `cd ui && npm run build` manually. Dev workflow: `gitbench render --format json && cd ui && npm run dev` for hot-reload during development.
- **[Trade-off] No JS fallback for charts** → Accepted: charts require JS. Users without JS see the static content (tables, text, cards) but not interactive charts. This is acceptable for a developer tool.
- **[Trade-off] Compare page is mostly React** → Accepted: the Compare page's entire content depends on model selection state, making it the one page where React dominates. It's still wrapped in the Astro Layout shell.

## Open Questions

- Whether to include Recharts or another chart library — settled on Recharts for its declarative React API and good defaults
- Whether the sidebar should be collapsible on mobile — assumed yes, standard responsive pattern
- Whether to support dark mode toggle or single theme — single dark theme matching current report aesthetic
