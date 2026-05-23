## Context

The GitBench web app currently has sort logic for reasoning effort levels and fixture difficulties duplicated across three locations:

- `model-groups.ts`: Defines `REASONING_LEVEL_ORDER` and `compareReasoningEfforts()` for chart grouping only
- `models/index.astro`: Defines its own local `LEVEL_ORDER` for the models listing page
- `models/[provider]/[model]/[level].astro`: Defines local `DIFF_ORDER` for fixture gallery difficulty filters

Two pages (`models/[provider]/[model]/index.astro` and `models/[provider]/[model]/[level].astro` tab bar) render levels without any sorting. `explore.astro` sorts difficulties alphabetically. The existing spec for report-pages already requires difficulty-sorted dropdowns on the drill-down page but is silent on level sorting and explore sorting.

## Goals / Non-Goals

**Goals:**
- Single source of truth for all ordinal sort orders (reasoning levels, difficulties)
- All model pages render effort levels in natural progression order
- All difficulty dropdowns sort by complexity, not alphabetically
- Existing `compareReasoningEfforts` in `model-groups.ts` delegates to the shared module

**Non-Goals:**
- Changing sort order of categorical data (tags, benchmarks)
- Adding sort controls or user-configurable sort
- Modifying the benchmark pipeline or Python code

## Decisions

### Decision 1: New shared module `lib/sort-orders.ts`

**Choice**: Create `gitbench/web/src/lib/sort-orders.ts` as the single home for ordinal sort constants.

```typescript
// lib/sort-orders.ts
export const REASONING_LEVEL_ORDER: Record<string, number> = {
  "": 0,
  none: 0,
  default: 0,
  low: 1,
  medium: 2,
  high: 3,
  xhigh: 4,
  max: 5,
};

export const DIFFICULTY_ORDER: Record<string, number> = {
  trivial: 0,
  easy: 1,
  medium: 2,
  hard: 3,
  expert: 4,
};

export function compareReasoningEfforts(
  a: string,
  b: string
): number {
  const aOrder = REASONING_LEVEL_ORDER[a] ?? 99;
  const bOrder = REASONING_LEVEL_ORDER[b] ?? 99;
  if (aOrder !== bOrder) return aOrder - bOrder;
  return a.localeCompare(b);
}
```

**Alternatives considered**:
- Export from `model-groups.ts`: Rejected — Astro pages shouldn't import from chart component internals
- Enum-based approach: Rejected — overkill; a simple Record<string,number> is sufficient and already established
- Inline in every page: Rejected — the problem we're fixing

### Decision 2: Sort levels directly, not through `ModelGroupEffort` wrapper

**Choice**: Astro pages will import `REASONING_LEVEL_ORDER` directly and use it in `.sort()` calls on `group.levels`, rather than going through `compareReasoningEfforts` which expects `MetricEffort` objects.

**Rationale**: Astro pages work with raw `BaseModelGroupLevel` objects, not `MetricEffort`. The sort is:

```typescript
group.levels.sort((a, b) => {
  const aOrder = REASONING_LEVEL_ORDER[a.level || ""] ?? 99;
  const bOrder = REASONING_LEVEL_ORDER[b.level || ""] ?? 99;
  return aOrder - bOrder;
})
```

This is identical to `compareReasoningEfforts` logic but operates on the right data shape.

### Decision 3: Update `model-groups.ts` to re-export from shared module

**Choice**: `model-groups.ts` will import `REASONING_LEVEL_ORDER` and `compareReasoningEfforts` from `sort-orders.ts`, and remove its own definitions. `compareReasoningEfforts` in `model-groups.ts` will become a thin wrapper that delegates string comparison to the shared function while retaining the `MetricEffort`-specific field extraction.

**Rationale**: Avoids duplicating the mapping in two places while preserving the existing call signature for all chart consumers.

## Risks / Trade-offs

- **Risk: `level` field could be null** → Mitigation: use `a.level || ""` as the sort key, falling through to the `""` entry (order 0). This matches existing behavior in `models/index.astro` which uses `l.level || "none"`.
- **Risk: Astro frontmatter can't import TypeScript directly** → Not an issue: Astro `.astro` files support `import` statements in frontmatter that resolve `.ts` modules with the existing `tsconfig.json` path aliases.
- **Risk: Build cache may need invalidation** → Non-issue: pure display change, no data mutation.
