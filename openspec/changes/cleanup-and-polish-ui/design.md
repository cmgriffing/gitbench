## Context

The Astro report UI (`gitbench/web/`) is a static site generated at build time by `gitbench report`. It uses Astro for layout and static content, React islands for interactive components (charts, model selection), and Recharts for chart rendering. All styling is done via raw CSS custom properties and inline `style="..."` attributes. The Python side (`gitbench/render.py`) still contains ~820 lines of unreachable HTML generation code from the pre-Astro era.

This change is a cleanup + polish pass: remove dead code, adopt a proper design system (shadcn/ui + Tailwind), replace the cramped model selector with a searchable dropdown, and swap unicode emoji icons for Lucide.

The existing `astro-report-ui` change has 4 remaining tasks (1.8, 12.3, 12.6, 12.7) that are rolled into this change.

## Goals / Non-Goals

**Goals:**
- Remove all dead `render_html` code from `render.py` and obsolete tests from `test_render.py`
- Delete stale project root artifacts (`index.html`, report screenshots)
- Install and configure shadcn/ui with Tailwind CSS in the Astro project
- Convert inline styles to shadcn components (Card, Badge, Button) and Tailwind utility classes
- Replace `ModelSelector` with a Command+Popover searchable multi-select
- Replace unicode emoji sidebar icons with Lucide icons
- Write tests for `render_json()` and new aggregation fields
- Update `CONTRIBUTING.md` and `README.md`

**Non-Goals:**
- Changing the Astro SSG architecture or adding SSR
- Adding new page routes beyond the existing seven
- Changing the data pipeline (`aggregate_runs()` → `render_json()` → Astro static build)
- Adding dark/light theme toggle (stays dark theme only)
- Animations or transitions beyond shadcn defaults
- Grouped/hierarchical model selector — flat list with search only

## Decisions

### Decision 1: shadcn/ui via manual setup with Tailwind v4

**Rationale:** shadcn/ui is the most widely adopted React component library with excellent dark theme support, keyboard navigation, and accessibility baked in. For Astro, we use manual setup (`npx shadcn@latest init`) configured to output components into `gitbench/web/src/components/ui/`. Tailwind v4 (zero-config by default, no `tailwind.config.ts` needed for basic usage) is used for utility classes. The existing CSS custom properties (`--bg`, `--accent`, etc.) are mapped into Tailwind's theme extension so shadcn components inherit the existing dark palette.

**Alternatives considered:**
- Radix UI primitives directly — rejected; shadcn is built on Radix and provides ready-to-use styled components, avoiding the need to style every primitive
- Keep raw CSS with custom components — rejected; doesn't solve consistency, doesn't give us Command/Search for free
- Tailwind v3 with config file — rejected; v4 is the current stable release and simplifies setup

### Decision 2: shadcn React components used directly in Astro, no wrappers needed

**Rationale:** Astro can render React components server-side without any `client:*` directive — they become static HTML with zero JavaScript. Since shadcn's Card, Badge, and Button are pure presentational components (no hooks, no state, no effects), they can be imported and used directly in `.astro` files:

```astro
---
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
---
<Card>
  <CardHeader><CardTitle>Model Summary</CardTitle></CardHeader>
  <CardContent>
    <Badge variant="outline">gpt-4o</Badge>
  </CardContent>
</Card>
```

This works because Astro's server-side rendering handles React components natively. The output is pure HTML with Tailwind classes — no hydration, no client JS. Only interactive components (ModelSelector with Command+Popover, Select dropdowns) need `client:load`.

We add a path alias `@` → `src/` in `tsconfig.json` for clean imports.

**Alternatives considered:**
- Create separate `.astro` wrappers for Card/Badge/Button — rejected; unnecessary duplication, shadcn React components work directly
- `client:load` on all shadcn components — rejected; wasteful, sends JS for static content

### Decision 3: Searchable multi-select via Command + Popover

**Rationale:** The current ModelSelector is a flat row of `<label>` pills with hidden checkboxes. With 10+ model entries (each model+reasoningLevel is a separate entry), this becomes visual noise. A Command-based dropdown provides:

1. A compact trigger showing selected count ("3 selected") or model names
2. A search input that filters the flat list as you type
3. Checkbox items with visual selection state
4. "Select all" / "Clear all" convenience actions at the top

The list remains flat (no grouping by base model) per the user's preference. Search by substring match on `model.name` is sufficient for navigation.

**Alternatives considered:**
- Multi-select with grouped headings (baseModel → reasoningLevels) — rejected by user; flat is simpler and preferred
- Tag-style input with autocomplete — rejected; Command dropdown is a more familiar pattern
- Keep current pill layout but add search — rejected; the pill layout doesn't visually communicate "multi-select" well

### Decision 4: Lucide icons via `lucide-react` rendered server-side in Astro

**Rationale:** The Sidebar is an Astro component (`.astro`). Since Astro can render React components server-side without hydration, we import Lucide icons from `lucide-react` and use them directly:

```astro
---
import { LayoutDashboard, Cpu, BarChart3, Search, GitCompare, History } from 'lucide-react';
---
<LayoutDashboard size={18} strokeWidth={2} />
```

These render to static inline SVGs with zero client JS. We use `lucide-react` (not `lucide-static`) because: (1) it's the canonical package, (2) Astro handles React component rendering natively on the server, and (3) it provides the same declarative API we use elsewhere. The icons inherit `currentColor` automatically for active/hover states.

**Alternatives considered:**
- `lucide-static` (raw SVG strings) — rejected; Astro renders React natively, no need for a separate package
- React island wrapper — rejected; unnecessary `client:load` for static icons

**Icon mapping:**
| Old (unicode) | New (Lucide) | Icon name |
|---|---|---|
| ◉ Dashboard | `LayoutDashboard` | layout-dashboard |
| ◇ Models | `Cpu` | cpu |
| ▦ Benchmarks | `BarChart3` | bar-chart-3 |
| ◎ Explore | `Search` | search |
| ⨯ Compare | `GitCompare` | git-compare |
| ◷ History | `History` | history |

**Alternatives considered:**
- `lucide-react` in a React island — rejected; unnecessary runtime JS for static icons
- Keep unicode emoji — rejected; inconsistent cross-platform rendering

### Decision 5: Dead code removal is all-or-nothing

**Rationale:** The `render_html()` function and its helper `render_html_from_envelope()` have zero callers outside of tests. The CLI no longer has a `render` subcommand (only `report`). The `index.html` in the project root is a stale artifact from a previous manual run. There's no reason to keep any of it. Tests that exercise dead code provide false confidence and create maintenance burden.

**Files to delete/modify:**
- `gitbench/render.py`: remove `render_html()` (lines 322–1127) and `render_html_from_envelope()` (lines 1128–1143)
- `tests/test_render.py`: remove `TestRenderHtml` (5 tests), `TestRenderCommand` (7 tests), `TestRenderReasoningLevel` (5 tests). Keep `TestLoadRunsFromDir`, `TestLoadRunsFromJsonl`, and `TestAggregateRuns` — these test the still-live `aggregate_runs()` pipeline
- Project root: delete `index.html`, `gitbench-manrope.png`, `gitbench-no-overall.png`, `gitbench-report-new.png`, `gitbench-report-original.png`, `gitbench-report-wide.png`

**Alternatives considered:**
- Deprecation warning before removal — rejected; no external consumers, the old CLI path is already gone

## Risks / Trade-offs

- **[Risk] Tailwind CSS conflicts with existing CSS custom properties** → Mitigation: Map existing design tokens into Tailwind theme. The custom properties stay but become a Tailwind preset, not standalone styles. Global styles (body background, fonts) stay in `global.css` above the `@tailwind` directives.
- **[Risk] shadcn components in Astro island have SSR mismatch** → Mitigation: shadcn components are client-rendered in React islands. The Astro page shell renders server-side, and the interactive islands hydrate on the client. This is the standard Astro pattern and causes no mismatch.
- **[Trade-off] shadcn components are React, Astro pages are .astro** → Accepted: Astro server-renders React components to static HTML with zero client JS for non-interactive components (Card, Badge, Button). The design system is unified — there aren't two Card implementations to maintain.

## Migration Plan

1. This change is self-contained — no external consumers to migrate
2. After implementation, `gitbench report` works identically from the user's perspective (same CLI, same static output)
3. If the Astro build breaks, revert by restoring `render.py` from git history (no data migration needed)
4. Old `index.html` and screenshots are purely cosmetic cleanup — deleting them has no functional impact

## Open Questions

- Whether to install additional shadcn components beyond the initial six (Card, Badge, Button, Select, Command, Popover) — determined during implementation as needed
- Whether `input.tsx` or `scroll-area.tsx` shadcn components are useful for the multi-select — Command includes its own Input and scroll handling, so likely not needed
