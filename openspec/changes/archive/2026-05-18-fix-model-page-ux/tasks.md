## 1. Fix fixture gallery filter JavaScript

- [x] 1.1 Strip TypeScript syntax from inline `<script>` in `[level].astro`: remove `as HTMLSelectElement` casts, `: any` annotations, and `forEach((card: any)` annotations
- [x] 1.2 Verify: open a model level page in the browser, select a benchmark filter → only matching fixture cards visible
- [x] 1.3 Verify: select multiple filters (benchmark + difficulty) → AND logic works
- [x] 1.4 Verify: click Reset → all filters clear and all cards visible

## 2. Sort difficulty dropdown by difficulty order

- [x] 2.1 Add `DIFF_ORDER` map (`{ trivial: 0, easy: 1, medium: 2, hard: 3, expert: 4 }`) in `[level].astro`
- [x] 2.2 Replace `Array.from(diffs).sort()` with custom comparator using `DIFF_ORDER`, falling back to alphabetical for unknown values
- [x] 2.3 Verify: difficulty dropdown renders options as trivial, easy, medium, hard, expert (not alphabetical)

## 3. Fix button outline/ghost hover text color

- [x] 3.1 In `button.tsx`, change outline variant hover from `hover:bg-accent hover:text-accent-foreground` to `hover:bg-accent/20 hover:text-accent`
- [x] 3.2 In `button.tsx`, change ghost variant hover from `hover:bg-accent hover:text-accent-foreground` to `hover:bg-accent/10 hover:text-accent`
- [x] 3.3 Verify: hover over Compare button on model level page → text stays cyan, background gets subtle tint
- [x] 3.4 Verify: hover over any other outline/ghost button across the site → no black text on hover

## 4. Split token display in model level header

- [x] 4.1 In `[level].astro`, compute separate `totalInputTokens` and `totalOutputTokens` sums from `fx.input_tokens` and `fx.output_tokens`
- [x] 4.2 Replace the single `totalTokens.toLocaleString() tokens` display with formatted input/output split (e.g., `"X in / Y out tokens"`)
- [x] 4.3 Verify: model level page header shows separate input and output token counts
- [x] 4.4 Verify: models with no token data show no token summary (existing behavior preserved)

## 5. Final verification

- [x] 5.1 Run `pnpm run build` in `gitbench/web/` to confirm no build errors
- [x] 5.2 Spot-check: navigate `/models/[provider]/[model]/[level]/` for a model with fixture data, confirm all four fixes work together
