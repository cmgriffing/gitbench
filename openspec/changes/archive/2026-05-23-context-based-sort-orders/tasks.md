## 1. Create shared sort orders module

- [x] 1.1 Create `gitbench/web/src/lib/sort-orders.ts` with `REASONING_LEVEL_ORDER`, `DIFFICULTY_ORDER` constants, and `compareReasoningLevels` helper
- [x] 1.2 Export `compareReasoningLevels(a: string, b: string): number` for use by Astro pages (compares normalized level strings using `REASONING_LEVEL_ORDER`)

## 2. Update model-groups.ts to delegate to shared module

- [x] 2.1 Remove local `REASONING_LEVEL_ORDER` Map from `model-groups.ts`
- [x] 2.2 Import `REASONING_LEVEL_ORDER` and `compareReasoningLevels` from `sort-orders.ts`
- [x] 2.3 Update `compareReasoningEfforts` in `model-groups.ts` to delegate string comparison to `compareReasoningLevels` while retaining `MetricEffort`-specific field extraction

## 3. Fix effort level sorting on model pages

- [x] 3.1 In `models/[provider]/[model]/index.astro`: import `REASONING_LEVEL_ORDER` from `sort-orders.ts` and sort `group.levels` by level before rendering cards
- [x] 3.2 In `models/[provider]/[model]/[level].astro`: import `REASONING_LEVEL_ORDER` from `sort-orders.ts` and sort `group.levels` by level before rendering the tab bar
- [x] 3.3 In `models/index.astro`: replace local `LEVEL_ORDER` with import from `sort-orders.ts`

## 4. Fix difficulty sorting on explore page

- [x] 4.1 In `explore.astro`: import `DIFFICULTY_ORDER` from `sort-orders.ts` and replace `Array.from(allDiffs).sort()` with difficulty-order sort
- [x] 4.2 In `models/[provider]/[model]/[level].astro`: replace local `DIFF_ORDER` with import from `sort-orders.ts`

## 5. Verify

- [x] 5.1 Run `npm run build` in `gitbench/web/` and confirm no build errors
- [x] 5.2 Visually inspect model pages to confirm levels appear in effort order
- [x] 5.3 Visually inspect explore page and drill-down page to confirm difficulty dropdowns sort by complexity
