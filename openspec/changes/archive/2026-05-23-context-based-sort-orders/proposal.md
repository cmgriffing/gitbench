## Why

Two model pages render reasoning effort levels in arbitrary (JSON) order instead of their natural progression (none → low → medium → high → xhigh → max). The Explore page's difficulty dropdown sorts alphabetically rather than by complexity. Meanwhile, a shared sort utility (`compareReasoningEfforts`) already exists in `model-groups.ts` but goes unused by the Astro pages, and three separate `LEVEL_ORDER`/`DIFF_ORDER` constants are scattered across the codebase. Fixing this now prevents user confusion and eliminates the risk of future pages forgetting to sort.

## What Changes

- Extract `REASONING_LEVEL_ORDER` and `DIFFICULTY_ORDER` into a shared `lib/sort-orders.ts` module
- Export `compareReasoningEfforts` from the same module (currently in `model-groups.ts`)
- Apply level sorting to `models/[provider]/[model]/index.astro` (currently unsorted)
- Apply level sorting to `models/[provider]/[model]/[level].astro` tab bar (currently unsorted)
- Apply difficulty sorting to `explore.astro` difficulty dropdown (currently alphabetical)
- Replace local `LEVEL_ORDER` in `models/index.astro` and local `DIFF_ORDER` in `[level].astro` with imports from the shared module
- Update `model-groups.ts` to import from `sort-orders.ts` instead of owning the constants

## Capabilities

### Modified Capabilities
- `report-pages`: Reasoning levels on base model overview and level drill-down pages SHALL be sorted by effort order. Difficulty dropdown on Explore page SHALL be sorted by difficulty order.

## Impact

- **Affected files**: `lib/sort-orders.ts` (new), `model-groups.ts`, `models/index.astro`, `models/[provider]/[model]/index.astro`, `models/[provider]/[model]/[level].astro`, `explore.astro`
- **No API changes, no data changes, no breaking changes**
- Display-only reordering — zero risk to data integrity
