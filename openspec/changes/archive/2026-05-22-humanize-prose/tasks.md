## 1. Info-Toggle Infrastructure

- [x] 1.1 Add `.info-toggle` CSS to `global.css` (hide default triangle, ⓘ icon on desktop via `::after`, hide icon on mobile via media query)
- [x] 1.2 Add inline `<script>` to `Layout.astro` that closes all `details.info-toggle[open]` when viewport > 768px

## 2. Overview Page (`index.astro`)

- [x] 2.1 Rewrite About section prose in conversational voice: shorter sentences, fragments, contractions, no emdashes, no "Learn more →" link
- [x] 2.2 Delete blurb from Model Summary (Pass Rate) section
- [x] 2.3 Delete blurb from Cost per Full Run section
- [x] 2.4 Delete blurb from Token Usage section
- [x] 2.5 Convert Quadrant Comparison blurb to `<details class="info-toggle" open>` with rewritten conversational text
- [x] 2.6 Convert Runtime blurb to `<details class="info-toggle" open>` with rewritten conversational text (keep the latency caveat)
- [x] 2.7 Convert Benchmark Matrix blurb to `<details class="info-toggle" open>` with rewritten conversational text

## 3. Explore Page (`explore.astro`)

- [x] 3.1 Convert top blurb to `<details class="info-toggle" open>` with rewritten conversational text

## 4. Compare Page (`compare.astro`)

- [x] 4.1 Convert top blurb to `<details class="info-toggle" open>` with rewritten conversational text (keep the head-to-head disagreement insight)

## 5. Benchmarks Pages

- [x] 5.1 Delete top blurb from `benchmarks/index.astro`
- [x] 5.2 Convert Model Leaderboard blurb to `<details class="info-toggle" open>` on `benchmarks/[name].astro` with rewritten conversational text
- [x] 5.3 Delete Per-Fixture Comparison blurb from `benchmarks/[name].astro`

## 6. Models Pages

- [x] 6.1 Rewrite top blurb on `models/index.astro` (always-visible, keep hierarchy explanation, conversational voice)
- [x] 6.2 Delete top blurb from `models/[provider]/[model]/index.astro`
- [x] 6.3 Delete Fixture Gallery blurb from `models/[provider]/[model]/[level].astro`

## 7. History Page (`history.astro`)

- [x] 7.1 Delete Pass Rate Over Time blurb
- [x] 7.2 Convert Run Log blurb to `<details class="info-toggle" open>` with rewritten conversational text (keep the delta explanation)

## 8. Fixture Detail Page (`fixtures/[benchmark]/[fixture].astro`)

- [x] 8.1 Rewrite Baseline Repository blurb (always-visible, conversational voice)
- [x] 8.2 Delete Model Outputs blurb

## 9. Chart Tooltip Footnotes

- [x] 9.1 Tighten `PassRateBarChart` tooltip footnote to "% of 204 fixtures passed"
- [x] 9.2 Tighten `CostValueChart` tooltip footnote to "API cost for 204-fixture run. — = local/Ollama"
- [x] 9.3 Tighten `RuntimeBarChart` tooltip footnote to "Wall-clock time. Includes API latency."
- [x] 9.4 Tighten `TokenUsageChart` tooltip footnote to "Tokens in + out. Fewer is more efficient."
- [x] 9.5 Tighten `TimeSeriesChart` tooltip footnote to "Pass rate on this date."
- [x] 9.6 Remove tooltip separator + footnote from `ScatterPlot`
- [x] 9.7 Remove tooltip separator + footnote from `QuadrantComparisonChart`

## 10. Verification

- [x] 10.1 Verify no emdashes (—) remain in prose outside Methodology page
- [x] 10.2 Verify no "Learn more" links remain in blurbs outside Methodology page
- [x] 10.3 Verify toggles are closed on desktop viewport and open on mobile viewport
- [x] 10.4 Build the site and spot-check all 10 pages for conversational voice and correct blurb placement
