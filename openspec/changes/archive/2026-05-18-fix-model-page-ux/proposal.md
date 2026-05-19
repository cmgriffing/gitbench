## Why

The model detail page has three bugs that degrade the user experience: the fixture gallery filters are completely broken (TypeScript syntax in a plain `<script>` tag causes a JavaScript error), difficulty values sort alphabetically instead of by actual difficulty order, and the button component's `outline` variant renders black text on hover due to a misconfigured design token. Additionally, the token summary in the page header only shows a monolithic total — users want to see the split between input and output tokens.

## What Changes

- **Fix fixture gallery filter JavaScript** — Strip TypeScript type assertions (`as HTMLSelectElement`, `: any`) from the inline `<script>` in `[level].astro` so the browser can actually execute it
- **Fix difficulty sort order** — Replace `Array.from(diffs).sort()` with a custom comparator using a defined difficulty order (`trivial` → `easy` → `medium` → `hard` → `expert`)
- **Fix button outline/ghost hover text** — Change `hover:bg-accent hover:text-accent-foreground` to `hover:bg-accent/20 hover:text-accent` in the `button.tsx` CVA variants so text remains readable (cyan) on a subtle tinted background instead of flipping to near-black
- **Split token display in header** — Compute separate `inputTokensTotal` and `outputTokensTotal` sums in the model level page and display them as `"X in / Y out tokens"` instead of the single `totalTokens` number. The per-fixture `FixtureCard` already shows individual input/output — this mirrors that breakdown at the summary level.

## Capabilities

### New Capabilities
<!-- No new capabilities — these are bug fixes and a minor display enhancement within existing page structure -->

### Modified Capabilities
- `report-pages`: The model level drill-down page's fixture gallery filter behavior and token summary display are changing. The spec says "Fixture gallery filters work" — this change makes that scenario actually pass.
- `shadcn-ui`: The Button component's outline and ghost variant hover colors are changing to avoid black text on hover.

## Impact

- `gitbench/web/src/pages/models/[provider]/[model]/[level].astro` — fixture filter JS fix, difficulty sort fix, token split display
- `gitbench/web/src/components/ui/button.tsx` — outline and ghost variant hover color change
