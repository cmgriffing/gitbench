## Context

The model level drill-down page (`[level].astro`) renders fixture cards inside a filterable gallery. An inline `<script>` provides client-side filtering, and the page header shows aggregate token counts. The `Button` component from shadcn/ui provides outline and ghost variants used across the site.

Three bugs were identified during manual testing, plus a display enhancement:

1. **Filter JS silent failure**: The `<script>` tag contains TypeScript syntax (`as HTMLSelectElement`, `: any`) that the browser cannot parse
2. **Difficulty lexicographic sort**: `Array.from(diffs).sort()` yields alphabetical order (easy, expert, hard, medium, trivial) instead of difficulty order (trivial, easy, medium, hard, expert)
3. **Button hover black text**: The outline variant's `hover:bg-accent hover:text-accent-foreground` pairs a cyan background with near-black text because `--color-accent-foreground` is `#07090f`
4. **Token summary not split**: The header only shows `totalTokens.toLocaleString()` — but per-fixture `input_tokens`/`output_tokens` data already exists

## Goals / Non-Goals

**Goals:**
- Make fixture gallery filters actually work by fixing the script's JavaScript syntax
- Sort difficulty values by a defined difficulty order
- Fix the button outline/ghost hover so text stays readable on the dark theme
- Display input/output token breakdown in the page header summary

**Non-Goals:**
- No changes to the Python harness (reasoning_tokens collection, etc.)
- No new shadcn components
- No changes to other pages that use the same Button variants (fix is at component level)
- No changes to how fixture cards render (already correct)

## Decisions

### Decision 1: Fix the inline script by converting to plain JS
**Chose**: Strip all TypeScript syntax — `as HTMLSelectElement` → remove cast, `: any` → remove annotation, `forEach((card: any)` → `forEach(function(card)`.

**Alternative considered**: Move filter logic to a React island. Rejected as overkill — the filtering is simple DOM manipulation that works fine as vanilla JS. No state management or framework needed.

### Decision 2: Difficulty sort using a static order map
**Chose**: Define a `DIFF_ORDER` object `{ trivial: 0, easy: 1, medium: 2, hard: 3, expert: 4 }` and sort with it.

**Alternative considered**: Using the existing `REASONING_LEVEL_ORDER` map from `model-groups.ts`. Rejected because that maps reasoning levels (low/medium/high), not difficulty levels (easy/medium/hard). The difficulty domain is separate.

### Decision 3: Button hover fix at component level using transparency
**Chose**: Change outline variant to `hover:bg-accent/20 hover:text-accent` and ghost to `hover:bg-accent/10 hover:text-accent`. This keeps the text cyan on a subtle tinted background, avoiding any black text.

**Alternative considered**: Change `--color-accent-foreground` in the design tokens to white. Rejected because that would also affect the primary button variant (`bg-primary text-primary-foreground`) which expects dark text on cyan — changing it to white would make primary buttons hard to read.

### Decision 4: Token split in page header only
**Chose**: Sum `input_tokens` and `output_tokens` separately from the fixture results and display as `"X in / Y out tokens"`. Reasoning tokens excluded from this change since they're not in the data.

**Alternative considered**: Also updating the TokenUsageChart. Not needed — the chart already shows input/output in its tooltips and uses a different aggregation path.

## Risks / Trade-offs

- **Outline/Ghost hover change affects all pages**: Since this is a component-level button change, every outline/ghost button across the site will get the new hover behavior. Risk: some page may have relied on the old behavior. Mitigation: the new behavior (subtle tint + cyan text) is more conservative than the old one (solid accent bg + black text), so it's unlikely to break any layout. The Compare button on the model page was the main use case.
- **Difficulty sort relies on known values**: If a new difficulty value is added (e.g. "impossible"), it falls to position 99 (after expert). Risk: unknown values sort last. Mitigation: this is acceptable — new difficulties get added to the map when they're introduced.
