## Context

The model/effort drill-down page (`[level].astro`) is an Astro SSG page. At build time, it renders fixture cards from `data.fixtures[modelName]` where `modelName = textModelName || jsonModelName` (preferring text). The page has:

1. **Header stats** — computed at build time from `data.model_summaries[modelName]` (text by default)
2. **ModelReliabilitySummary** — a React island (`client:load`) that fetches `/api/models/{model}/results?output_mode={mode}` with a hardcoded `outputMode` prop
3. **Text vs JSON Comparison** — static Astro section, only renders when both modes exist
4. **Fixture Gallery** — static Astro cards + vanilla JS filtering (benchmark, difficulty, tag)

Both text and JSON fixture results exist in the build-time data (`data.fixtures[textModelName]` and `data.fixtures[jsonModelName]`). The existing `OutputModeSelector` React component (used on the Compare page) provides Text/JSON/Both buttons with localStorage persistence via `readStoredOutputMode()` / `writeStoredOutputMode()` in `model-groups.ts`.

## Goals / Non-Goals

**Goals:**
- Page-wide output mode toggle on the model/effort page controlling header stats, reliability summary, and fixture gallery
- Toggle uses the same `gitbench-output-mode` localStorage key as the rest of the site
- Compact "Both" mode fixture cards with stacked text/JSON scores (no token details)
- Header stats toggle between text and JSON; "Both" shows both stacked
- Reliability summary refetches on toggle change
- No API changes — all data is available at build time or via existing API

**Non-Goals:**
- Changing the "Text vs JSON Comparison" section — it stays as-is
- Converting the fixture gallery to a React component — stays Astro SSG + vanilla JS
- Adding JSON-specific card info (parsed payload, structured error) — just the score
- Server-side rendering or dynamic API calls for fixture cards — pre-rendered at build time

## Decisions

### Decision 1: Pre-render all three card sets, toggle visibility client-side

**Rationale:** The page is Astro SSG and the data is available at build time in `results.json`. Pre-rendering three card sets (text, JSON, both) and toggling visibility with vanilla JS is the simplest approach that preserves the SSG model. No API calls needed for fixture cards, no loading states, instant toggle. The page weight increase is manageable — fixture cards are small (~200 bytes HTML each), and the gallery has ~200 fixtures per model effort.

**Alternatives considered:**
- React component with API fetch — rejected; overkill for static data, adds loading states, breaks SSG for the main gallery content
- Hybrid (pre-render default, fetch on toggle) — rejected; unnecessary complexity when all data is available at build time

### Decision 2: Vanilla JS toggle instead of React OutputModeSelector

**Rationale:** The fixture gallery filtering is already vanilla JS. Adding a React island just for three buttons would create an awkward bridge between React state and vanilla JS DOM manipulation. A vanilla JS toggle (three styled buttons matching the filter bar aesthetic) that writes to the same localStorage key and dispatches a `CustomEvent` is simpler and consistent with the existing page architecture.

**Alternatives considered:**
- React `OutputModeSelector` island — rejected; requires event bridge to communicate with vanilla JS gallery, adds unnecessary React dependency to a section that doesn't need it
- URL query parameter for output mode — rejected; would require page reload on SSG, doesn't match the instant-toggle UX of the Compare page

### Decision 3: Reliability summary listens for custom event

**Rationale:** `ModelReliabilitySummary` is already a React island with `client:load`. It already accepts an `outputMode` prop and fetches from the API. To make it respond to the vanilla JS toggle, it needs to: (1) read localStorage for the initial mode instead of using the hardcoded prop, and (2) listen for a `CustomEvent("output-mode-change")` dispatched by the toggle. This is a small modification that leverages existing fetch logic.

**Alternatives considered:**
- Pre-render two reliability summary instances and toggle visibility — rejected; doubles API calls on page load, wasteful
- Convert reliability summary to vanilla JS — rejected; it's already React and works well; no reason to rewrite

### Decision 4: "Both" mode shows text reliability, not both

**Rationale:** In "Both" mode, the reliability summary shows text-mode results. The "Text vs JSON Comparison" section directly below already covers cross-mode deltas (gained, lost, unchanged, per-benchmark deltas). Duplicating that information in the reliability table would be redundant. The toggle's main value in the reliability section is switching between text-only and JSON-only views.

**Alternatives considered:**
- Stacked reliability tables (text + JSON) — rejected; redundant with comparison section
- Merged table with Text/JSON/Δ columns — rejected; biggest change, overlaps with comparison section

### Decision 5: Compact "Both" card drops token details

**Rationale:** The user wants compact cards in "Both" mode. The card shows fixture ID, benchmark, and stacked text/JSON scores (pass/fail + similarity %). Token details are omitted to keep the card small and scannable. Single-mode cards retain the full token display.

**Alternatives considered:**
- Keep token details in both mode — rejected; user wants compact
- Show text-mode tokens only — rejected; inconsistent, could confuse

### Decision 6: Header stats pre-rendered as separate blocks

**Rationale:** The header stats (pass rate, fixtures passed, tokens, cost) are computed at build time from `data.model_summaries`. Pre-rendering both text and JSON stat blocks and toggling visibility client-side is straightforward. In "Both" mode, both blocks are shown stacked (text first, then JSON), matching the card design pattern.

**Alternatives considered:**
- Fetch stats from API on toggle — rejected; unnecessary, data is available at build time
- Single merged stat block with both modes — rejected; would be cluttered, stacked blocks are cleaner

## Risks / Trade-offs

- **[Trade-off] Triple fixture card HTML** → Accepted: ~200 fixtures × 3 card variants = ~600 cards in HTML. Each card is ~200 bytes, so ~120KB additional HTML per page. Acceptable for a static site.
- **[Risk] Mismatched fixture sets between text and JSON** → Mitigation: In "Both" mode, if a fixture exists in one mode but not the other, show "—" for the missing score. This should be rare since the same benchmark suite is used for both modes.
- **[Risk] CustomEvent not received by React island** → Mitigation: Use `window.dispatchEvent` and `window.addEventListener` — standard DOM events that React islands can listen for via `useEffect`.
- **[Trade-off] Reliability summary shows text in "Both" mode** → Accepted: The comparison section below covers cross-mode deltas. Users wanting JSON-only reliability can switch to "JSON" mode.

## Open Questions

- None remaining — all design decisions have been made through exploration with the user.