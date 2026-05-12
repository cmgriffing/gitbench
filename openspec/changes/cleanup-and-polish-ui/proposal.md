## Why

The Astro report UI is functionally complete (66/70 tasks done) but suffers from two problems: (1) ~800 lines of dead Python HTML rendering code and 17 obsolete tests still sit in the codebase, and (2) the UI is built entirely with raw CSS and inline styles — no component primitives, unicode emoji for icons, and a flat pill-based model selector that doesn't scale. This change removes the dead code and levels up the UX with shadcn/ui components, Lucide icons, and a searchable multi-select.

## What Changes

- **BREAKING**: Remove `render_html()` and `render_html_from_envelope()` from `gitbench/render.py` (~820 lines)
- **BREAKING**: Remove obsolete `TestRenderHtml`, `TestRenderCommand`, and `TestRenderReasoningLevel` test classes from `tests/test_render.py` (17 tests)
- Delete stale artifacts from project root: `index.html` (111KB Python-generated report) and 5 old report screenshots (~8MB total)
- Install and configure shadcn/ui with Tailwind CSS in `gitbench/web/`
- Add shadcn component primitives: Card, Badge, Button, Select, Command, Popover
- Replace `ModelSelector.tsx` with a searchable multi-select using Command+Popover (flat list, no grouping)
- Replace unicode emoji sidebar icons (◉◇▦◎⨯◷) with Lucide icons
- Convert all inline `style="..."` across ~10 pages/astro components to shadcn components and Tailwind utilities
- Write tests for `render_json()` and new aggregation fields
- Update `CONTRIBUTING.md` and `README.md` with new report workflow

## Capabilities

### New Capabilities

- `shadcn-ui`: Tailwind CSS + shadcn/ui design system setup, component primitives (Card, Badge, Button, Select, Command, Popover) installed in `gitbench/web/src/components/ui/`
- `searchable-model-selector`: Command+Popover-based multi-select replacing the flat pill checkbox ModelSelector, with search filtering by model name
- `lucide-icons`: Lucide icon library replacing unicode emoji in Sidebar.astro and any other emoji icon usage

### Modified Capabilities

<!-- None — existing spec capabilities (astro-site, report-pages, chart-components, json-export) are not changing their requirements, only their implementation. -->

## Impact

- **Modified**: `gitbench/render.py` — remove `render_html()`, `render_html_from_envelope()`
- **Modified**: `tests/test_render.py` — remove obsolete test classes, add `render_json()` tests
- **Modified**: `gitbench/web/package.json` — add tailwindcss, postcss, autoprefixer, lucide-react, shadcn deps
- **Modified**: `gitbench/web/src/styles/global.css` — add Tailwind directives
- **Modified**: `gitbench/web/src/components/Sidebar.astro` — replace unicode with Lucide
- **Modified**: `gitbench/web/src/components/charts/ModelSelector.tsx` — full rewrite
- **Modified**: `gitbench/web/src/pages/*.astro` — replace inline styles with shadcn/Tailwind
- **Modified**: `gitbench/web/src/components/fixtures/*.astro` — replace inline styles
- **Modified**: `gitbench/web/src/components/Layout.astro` — minor adjustments
- **Modified**: `CONTRIBUTING.md`, `README.md` — update documentation
- **New**: `gitbench/web/tailwind.config.ts`, `postcss.config.js`, `components.json`
- **New**: `gitbench/web/src/lib/utils.ts`
- **New**: `gitbench/web/src/components/ui/*.tsx` — shadcn components
- **Deleted**: `index.html`, `gitbench-*.png` from project root
- **Dependencies**: tailwindcss, @tailwindcss/typography, postcss, autoprefixer, lucide-react, shadcn/ui packages (class-variance-authority, clsx, tailwind-merge)
