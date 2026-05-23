## Context

The `comprehensive-explanatory-text` change added section blurbs to every chart, table, and content area across 10 Astro pages. Each blurb follows a template: 1-3 sentences describing what's visible, an optional "Learn more →" link to methodology, and consistent `text-sm text-(--color-text-mid) leading-relaxed` styling. The CSS tooltip system (`.has-tooltip`, `data-tooltip`, ⓘ icons) was designed but never shipped — no instances exist in the codebase. Native `title` attributes on `<span>` elements are the only tooltips remaining.

The prose suffers from an "AI-generated documentation" voice: formal, hedgy, over-signposting, and templated. On mobile, the accumulated blurbs create a wall of gray text users must scroll past before reaching any data.

**Constraint**: Frontend-only changes. No backend, no CLI, no data pipeline modifications. Methodology page (`/methodology`) is left untouched.

## Goals / Non-Goals

**Goals:**
- Rewrite all page prose in a conversational, fragment-friendly, emdash-free voice
- Delete blurbs that describe what's already visible (chart labels, axes, badges)
- Convert remaining helpful-but-not-critical blurbs to a `<details>` toggle pattern
- Keep genuinely important context always-visible (About section, models hierarchy, fixture setup)
- Tighten chart tooltip footnotes to single conversational fragments
- Ensure mobile experience prioritizes data over prose

**Non-Goals:**
- Changing the methodology page (canonical documentation)
- Adding new pages, components, or dependencies
- Changing chart rendering logic or data flow
- Modifying the sidebar, layout, or global CSS system (beyond the toggle pattern)
- i18n, localization, or accessibility audit beyond what `<details>` provides natively

## Decisions

### Decision 1: Use native `<details>` for info toggles (not JS popovers, not `<dialog>`)

**Rationale**: `<details>` is a native HTML element with built-in open/close behavior, keyboard accessibility, and screen reader support. It requires zero JavaScript, zero CSS hacks for show/hide, and degrades gracefully. On desktop, a small inline script closes all toggles on load. On mobile (≤768px), toggles stay open — text flows inline without interaction. The `<summary>` element serves as the click target; a ⓘ pseudo-element on desktop signals "there's info here."

**Markup pattern**:
```html
<details class="info-toggle" open>
  <summary>
    <span class="section-label">Model Summary</span>
  </summary>
  <p class="info-blurb">Overall Git skill across 204 fixtures. Higher = better.</p>
</details>
```

**CSS behavior**:
```css
.info-toggle > summary {
  list-style: none;        /* hide default triangle */
  cursor: default;          /* desktop: clickable */
}
.info-toggle > summary::after {
  content: " ⓘ";
  font-size: 0.7rem;
  opacity: 0.4;
}
@media (max-width: 768px) {
  .info-toggle > summary::after {
    content: none;          /* mobile: no icon needed */
  }
}
```

**JS for desktop** (tiny inline script in Layout.astro or global):
```js
if (window.innerWidth > 768) {
  document.querySelectorAll('details.info-toggle[open]').forEach(d => d.open = false);
}
```

**Alternatives considered**:
- *React islands for popovers*: Overkill for text. Adds bundle weight and hydration latency.
- *CSS-only tooltips*: Don't work on mobile (no hover). Already rejected in previous change.
- *Always-visible blurbs*: Clutters mobile. The whole point of this change is to reduce that.
- *`<dialog>` elements*: Require JS for open/close, less semantic than `<details>`.

### Decision 2: Blurb classification — always-visible vs toggle vs deleted

Each section's blurb is classified by whether it tells the user something they can't see:

| Treatment | Criteria | Example |
|-----------|----------|---------|
| **Always-visible** | Critical orientation or non-obvious mechanics | Landing About section, models hierarchy, fixture setup commands |
| **Details toggle** | Helpful context but not essential | "Wall-clock time includes API latency" for Runtime chart |
| **Deleted** | Describes what's visually obvious | "Higher bars mean the model answered more Git tasks correctly" for a bar chart |

**Full mapping** (from exploration audit):

Always-visible (3):
- `index.astro` About section (rewritten, stays multi-paragraph)
- `models/index.astro` top blurb (hierarchy explanation, trimmed)
- `fixtures/[benchmark]/[fixture].astro` Baseline Repository blurb

Details toggle (7):
- `index.astro` Quadrant Comparison ("Pick two criteria. Shaded quadrant = optimal.")
- `index.astro` Runtime ("Wall-clock time. Includes API latency and rate limits.")
- `index.astro` Benchmark Matrix ("Green = strong, red = weak. Some models ace basics but struggle with rebase.")
- `explore.astro` top blurb ("204 test cases. Filter by tag, difficulty, or benchmark.")
- `compare.astro` top blurb ("Pick 2+ models. Disagreement is where you learn.")
- `benchmarks/[name].astro` Leaderboard ("A model that dominates overall might rank lower here. That's the point.")
- `history.astro` Run Log ("Green Δ = improved since last run. Red Δ = regressed.")

Deleted (9):
- `index.astro` Pass Rate, Cost, Token Usage
- `benchmarks/[name].astro` Per-Fixture
- `models/[provider]/[model]/index.astro` top blurb
- `models/[provider]/[model]/[level].astro` Fixture Gallery
- `history.astro` Pass Rate Over Time
- `fixtures/[benchmark]/[fixture].astro` Model Outputs
- `benchmarks/index.astro` top blurb

### Decision 3: Voice guidelines for all prose

All remaining and rewritten prose follows these rules:

1. **No emdashes.** Use periods, commas, or sentence breaks instead.
2. **Fragments welcome.** "Ballpark efficiency metric. Fewer tokens for same result = better." is valid.
3. **Contractions.** "it's", "don't", "that's" — not "it is", "do not", "that is".
4. **Be opinionated.** "That's the point." not "This reveals each model's true strengths and weaknesses per skill."
5. **No signposting.** Don't describe what's on the page. The user can see it.
6. **No "Learn more" links.** Methodology is in the sidebar.
7. **One thought per sentence.** Break compound sentences. "Each model gets tested across 204 fixtures. Isolated repos. No luck, no vibes."
8. **No hedging unless it matters.** "Includes API latency" is fine. "May include some API latency overhead in certain configurations" is not.

### Decision 4: Chart tooltip footnotes — keep but tighten to fragments

The separator + footnote pattern in React chart tooltips stays (it's contextual help, not page prose), but the text is tightened:

| Chart | Current | New |
|-------|---------|-----|
| PassRateBarChart | "Pass rate = % of 204 Git fixtures answered correctly. Higher reasoning levels typically score better." | "% of 204 fixtures passed" |
| CostValueChart | "Total API cost (USD) across all 204 fixtures. — means local/Ollama (no cost tracked)." | "API cost for 204-fixture run. — = local/Ollama" |
| RuntimeBarChart | (similar verbose tooltip) | "Wall-clock time. Includes API latency." |
| TokenUsageChart | "Total tokens (input + output) across all 204 fixtures. Less output for same accuracy = more efficient." | "Tokens in + out. Fewer is more efficient." |
| TimeSeriesChart | "Pass rate on this date. Changes may reflect model updates or benchmark suite changes." | "Pass rate on this date." |
| ScatterPlot | (verbose tooltip) | Drop footnote entirely |
| QuadrantComparisonChart | (verbose tooltip) | Drop footnote entirely |

### Decision 5: No new CSS classes or design system changes

The `<details>` toggle styling uses existing design tokens (`--color-text-mid`, `--color-text-dim`) and the `.section-label` class already in use. The ⓘ icon is a CSS `::after` pseudo-element — no new icon library, no SVG sprite, no font dependency. The `.info-blurb` class is the only new class and follows the existing `text-sm` pattern for consistency.

## Risks / Trade-offs

- **[<details> on desktop requires JS to close]**: The pattern needs ~5 lines of JS to close toggles on desktop. If JS fails, toggles stay open (same as mobile) — graceful degradation. Mitigation: script is inline in `<head>` or Layout, runs synchronously before paint.
- **[Blurb deletion may lose useful context]**: Some users might miss explanations for self-explanatory sections. Mitigation: methodology page covers everything in depth. Sidebar link is always available.
- **[Voice consistency across 10+ text blocks]**: Rewriting prose manually risks inconsistency. Mitigation: explicit voice guidelines (Decision 3), review all text in one sitting.
- **[Chart tooltip footnotes might be missed]**: Users who relied on the "Pass rate = % of..." footnote may not understand the metric. Mitigation: chart axes are labeled ("Pass Rate %", "Cost (USD)"), and methodology page explains metrics.

## Open Questions

None. All design decisions resolved during exploration. The section classification mapping, voice guidelines, and toggle pattern are fully specified.
