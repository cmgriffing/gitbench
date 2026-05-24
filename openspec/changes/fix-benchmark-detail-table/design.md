## Context

The benchmark detail page at `gitbench/web/src/pages/benchmarks/[name].astro` renders two data-bound sections: a `PassRateBarChart` React island and a server-rendered per-fixture comparison table. Both have defects. The chart uses global pass rates instead of per-benchmark data, and the table has a fixture ID mismatch that causes every cell to show "—". Additionally, the table renders all 117 models as columns with no model selector — unlike every other chart on the site, which uses a shared synced selection system built on `localStorage` + `CustomEvent`.

The existing synced model selection consists of:
- `ModelSelector.tsx` — searchable multi-select dropdown that reads/writes `gitbench-model-selection` in localStorage and broadcasts `model-selection-changed` events
- `useSyncedModelSelection.ts` — hook used by chart components to read the synced selection
- `model-groups.ts` — derives model groups from data, expands group selections to individual model names, provides metric extractors for charts

## Goals / Non-Goals

**Goals:**
- Fix the fixture ID mismatch so the table shows actual similarity percentages
- Fix PassRateBarChart to accept an optional `benchmarkName` prop and use per-benchmark data
- Give the fixture comparison table its own `ModelSelector` synced with the rest of the site
- Show individual reasoning efforts as sub-columns under model group headers

**Non-Goals:**
- Changing the ModelSelector component or syncing mechanism — they work correctly
- Adding model selection to the fixture detail page
- Changing how `PassRateBarChart` works on the Overview page (no `benchmarkName` → global, unchanged)
- Adding sorting or filtering to the table (beyond the model selector)

## Decisions

### Decision 1: Pass benchmarkName as a prop to PassRateBarChart

**Chosen:** Add an optional `benchmarkName?: string` prop. When present, compute pass rates from `matrix[model][benchmarkName].pass_at_k`. When absent, use existing `model_summaries[model].pass_at_k`.

**Alternatives considered:**
- *Separate chart component* — would duplicate 95% of the chart code. Rejected.
- *Data attribute / URL-based detection* — fragile and implicit. Rejected.
- *Wrapper component that pre-filters data* — adds unnecessary indirection. Rejected.

**Rationale:** The prop is explicit, backward-compatible (all existing usages are unchanged), and easy to test. The tooltip footnote adapts to show the correct fixture count (e.g., "12 fixtures" vs "204 fixtures").

### Decision 2: New React component for the table (FixtureComparisonTable)

**Chosen:** Extract the table into a new `FixtureComparisonTable.tsx` React client component, rendered as `<FixtureComparisonTable client:load benchName={benchName} />`.

**Alternatives considered:**
- *Keep table in Astro but add a separate ModelSelector island that communicates via events* — two islands with coordination lag, complex data passing. Rejected.
- *Use web components* — no existing pattern in the project. Rejected.
- *Pass the entire filtered model list as Astro props* — can't respond to selector changes without a full page reload. Rejected.

**Rationale:** The table needs React state to respond to model selection changes. Putting everything in one React component avoids coordination issues between Astro and React islands. The pattern matches how other components like `PassRateBarChart` and `BenchmarkHeatmap` work.

### Decision 3: Table column layout — grouped headers with per-effort sub-columns

**Chosen:** For each selected model group, render a parent `<th>` spanning all effort sub-columns, with individual `<th>` elements for each effort level underneath.

```
┌──────────────────────────────────────────┐
│          │ claude-opus-4.7              │
│ Fixture  ├────────┬────────┬─────────────┤
│          │ low    │ medium │ high        │
├──────────┼────────┼────────┼─────────────┤
│ f001     │ 90.0%  │ 95.0%  │ 100.0%      │
└──────────────────────────────────────────┘
```

**Alternatives considered:**
- *Flat columns without grouping* — makes it hard to associate efforts with their base model when many groups are selected.
- *One column per group showing range* — loses per-effort detail. The chart already shows range; the table is for precise per-effort comparison.

**Rationale:** Grouped headers provide visual hierarchy that matches the mental model (base model → reasoning effort). The `colspan` approach is straightforward HTML.

### Decision 4: Fixture ID fix — use `fi.id` not `fid`

**Chosen:** In the find call, use `fixture_index[key].id` instead of the raw key. The `id` field contains the bare fixture ID (`"f001"`) that matches `result.fixture_id`.

**Alternatives considered:**
- *Change the JSON export to use bare IDs as fixture_index keys* — would break fixture detail page routing which uses `/fixtures/[benchmark]/[fixture]`. Rejected.
- *Strip the prefix at find time* — same effect, but `fi.id` already exists and is more explicit.

**Rationale:** This is the simplest possible fix. The template already extracts `fi.id` as `shortId` and uses it for the link URL — it just uses the wrong variable in the `find`.

### Decision 5: Per-benchmark pass rate metric

**Chosen:** Add `benchPassRateMetric(effort, data, benchName)` to `model-groups.ts` that returns a `MetricEffort | null` by reading `data.matrix[effort.modelName][benchName].pass_at_k`. Use it in `PassRateBarChart` when `benchmarkName` is provided, falling through to `passRateMetric` when it's absent.

**Rationale:** Follows the existing metric extractor pattern. The `buildGroupedMetricRows` function already supports arbitrary extractors; we just need one that reads from `matrix` instead of `model_summaries`.

## Risks / Trade-offs

- **[Risk] PassRateBarChart tooltip footnote fixture count** — when filtered to one benchmark, the footnote should say e.g. "% of 12 fixtures passed" not "204". → Mitigation: count fixtures in `fixture_index` for the given benchmark, or use `matrix[model][bench].total`.
- **[Risk] FixtureComparisonTable data loading** — the component needs access to the full `results.json` to derive model groups and fixture data. → Mitigation: use `loadData()` (async fetch) just like all other chart components. The table loads in a `useEffect` on mount.
- **[Trade-off] Astro page loses static rendering of the table** — the table was previously server-rendered (though broken). Now it's a `client:load` island. → Acceptable: the table was already non-functional when server-rendered, and other pages (Compare, charts) are already client islands.

## Open Questions

- Should the fixture comparison table support the same "Select all / Clear" quick actions that the ModelSelector dropdown provides? → Yes, this is built into `ModelSelector` already.
