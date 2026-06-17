## Why

The model/effort drill-down page (`/models/[provider]/[model]/[level]/`) has a Fixture Gallery that only shows text-mode fixture results — even when both text and JSON-schema results exist for the same model effort. The page already has a "Text vs JSON Schema Comparison" section showing aggregate deltas, but the gallery itself is locked to text. The rest of the site (Compare page) has an output mode toggle (Text/JSON/Both) with localStorage persistence, but this page doesn't use it. Users wanting to browse JSON-mode fixture cards have no way to do so without navigating to individual fixture detail pages.

## What Changes

- Add a page-wide output mode toggle (Text/JSON/Both) to the model/effort drill-down page, placed in the Fixture Gallery filter bar
- Toggle uses the same `gitbench-output-mode` localStorage key as the rest of the site, so mode preference persists across pages
- Pre-render all three fixture card sets at build time (text cards, JSON cards, and compact "both" cards with stacked scores); toggle visibility client-side
- In "Both" mode, fixture cards show stacked text and JSON scores (T 87% ✓ / J 91% ✓) without token details — compact and scannable
- Header stats (pass rate, fixtures passed, tokens, cost) toggle between text and JSON summaries; in "Both" mode, both stat blocks are shown stacked
- `ModelReliabilitySummary` React island reads localStorage for initial mode and listens for a custom event to refetch on toggle change
- For models with no JSON-schema variant, the toggle is hidden entirely (matching existing `OutputModeSelector` behavior)
- The "Text vs JSON Schema Comparison" section is unchanged — it inherently covers both modes

## Capabilities

### Modified Capabilities

- `report-pages`: Model level drill-down page gains page-wide output mode toggle controlling header stats, reliability summary, and fixture gallery

## Impact

- **Modified**: `gitbench/web/src/pages/models/[provider]/[model]/[level].astro` — pre-render both text and JSON fixture card sets and header stat blocks; add vanilla JS toggle + output-mode-aware filtering
- **Modified**: `gitbench/web/src/components/ModelReliabilitySummary.tsx` — read localStorage for initial output mode, listen for `output-mode-change` custom event, refetch on change
- **Modified**: `gitbench/web/src/components/fixtures/FixtureCard.astro` — add compact "both" variant with stacked text/JSON scores (or a companion component)
- **No API changes**: All fixture data is already in `results.json` at build time; the `loadModelResults` API is already used by `ModelReliabilitySummary` and supports `output_mode` param
- **No new dependencies**: Uses existing vanilla JS patterns for filtering and existing localStorage key for persistence