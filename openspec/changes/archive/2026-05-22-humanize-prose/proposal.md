## Why

The `comprehensive-explanatory-text` change added section blurbs and tooltips to every page, but the result reads like AI-generated documentation — formal, hedgy, over-explaining, and templated. On mobile, the wall of gray text before every chart creates a poor experience. The prose needs to feel like a person wrote it, and it needs to not dominate the page.

## What Changes

- **Rewrite all page prose** in a conversational, fragment-friendly voice. No emdashes. No hedging. Shorter sentences.
- **Delete ~9 section blurbs** that describe what's already visible (bar charts titled "Token Usage" don't need a paragraph above them).
- **~7 remaining blurbs move to a `<details>` toggle** — closed on desktop (with a ⓘ icon trigger), always-open inline on mobile. Text is available but doesn't compete with data.
- **~3 critical sections stay always-visible** (landing page About, models hierarchy, fixture setup commands).
- **Tighten chart tooltip footnotes** in all 6 React chart components to one conversational fragment.
- **Remove all "Learn more →" links** from blurbs. Methodology is accessible from the nav sidebar.
- **Methodology page untouched** — it's the canonical documentation and already reads naturally.

## Capabilities

### New Capabilities
- `section-info-toggles`: Reusable `<details>`-based info toggle pattern. Desktop: closed by default with ⓘ icon. Mobile: open by default, text flows inline. Zero JS dependency (native HTML).
- `conversational-prose-voice`: Style guidelines for all UI prose — conversational, fragment-friendly, opinionated, emdash-free. Applies to blurbs, tooltip footnotes, empty states, and any future text.

### Modified Capabilities
- `astro-site`: Section blurbs across all 10 Astro pages restructured — many removed, some converted to toggles, a few rewritten as always-visible. Old mandatory-blurb requirements from the previous explanatory-text change are reversed.
- `chart-components`: Tooltip footnote text in PassRateBarChart, CostValueChart, RuntimeBarChart, TokenUsageChart, TimeSeriesChart, ScatterPlot, and QuadrantComparisonChart tightened to conversational fragments.

## Impact

- **Affected code**: 8 Astro page files (`index.astro`, `explore.astro`, `compare.astro`, `benchmarks/index.astro`, `benchmarks/[name].astro`, `models/index.astro`, `models/[provider]/[model]/index.astro`, `models/[provider]/[model]/[level].astro`, `history.astro`, `fixtures/[benchmark]/[fixture].astro`), 2 fixture components (`FixtureCard.astro` with blurb), 6 React chart components
- **New pattern**: `<details class="info-toggle">` with responsive open/closed behavior
- **No API changes, no backend changes, no new dependencies**
- **Breaking**: None — all changes are subtractive or rewritten text, same structure preserved
