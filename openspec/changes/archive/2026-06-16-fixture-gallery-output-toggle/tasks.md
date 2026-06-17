## 1. Build-time fixture card pre-rendering

- [x] 1.1 In `[level].astro`, build `jsonFixtures` array from `data.fixtures[jsonModelName]` (when `jsonModelName` exists), matching the existing `allFixtures` text array structure
- [x] 1.2 Build `bothFixtures` array by merging text and JSON fixture results per fixture ID + benchmark, carrying both similarity/pass values
- [x] 1.3 Render three card sets in the gallery grid: text cards (`data-mode="text"`), JSON cards (`data-mode="json"`), and both cards (`data-mode="both"`)
- [x] 1.4 Add `data-benchmark`, `data-difficulty`, `data-tags` attributes to all three card sets so existing filter logic applies to whichever set is visible

## 2. Compact "Both" fixture card

- [x] 2.1 Add a "both" variant to `FixtureCard.astro` (or create a `FixtureCardBoth.astro` companion) that shows: fixture ID, benchmark, stacked text score ("T 87% ✓") and JSON score ("J 91% ✓"), with "—" for missing mode
- [x] 2.2 The both card links to the same fixture detail page as single-mode cards

## 3. Build-time header stats pre-rendering

- [x] 3.1 In `[level].astro`, compute header stats for both text model (`textModelName`) and JSON model (`jsonModelName`) when both exist
- [x] 3.2 Render two stat blocks: one with `data-stats="text"` (visible by default) and one with `data-stats="json"` (hidden by default)
- [x] 3.3 In "Both" mode, show both stat blocks stacked (text first, then JSON)

## 4. Vanilla JS output mode toggle

- [x] 4.1 Add three-button toggle (Text/JSON/Both) to the fixture gallery filter bar, styled to match existing filter controls
- [x] 4.2 On page load, read `localStorage.getItem("gitbench-output-mode")` and apply initial visibility (default to "text" if not set)
- [x] 4.3 On toggle change: write to `localStorage.setItem("gitbench-output-mode", mode)`, swap card set visibility, swap header stats visibility, and dispatch `window.dispatchEvent(new CustomEvent("output-mode-change", { detail: { mode } }))`
- [x] 4.4 Hide the toggle entirely when `jsonModelName` is null (model has no JSON variant)
- [x] 4.5 Ensure existing filter logic (benchmark/difficulty/tag) applies to whichever card set is currently visible — the `data-benchmark`/`data-difficulty`/`data-tags` attributes must be consistent across all three card sets

## 5. ModelReliabilitySummary React island update

- [x] 5.1 Modify `ModelReliabilitySummary.tsx` to read initial `outputMode` from `localStorage.getItem("gitbench-output-mode")` instead of relying solely on the `outputMode` prop (prop becomes fallback/default)
- [x] 5.2 Add `useEffect` that listens for `window.addEventListener("output-mode-change", ...)` and updates internal `outputMode` state
- [x] 5.3 The existing `useEffect([model, outputMode, campaignId])` fetch logic already handles refetching — no change needed there
- [x] 5.4 In "both" mode, the reliability summary SHALL use "text" for its fetch (the comparison section below handles cross-mode deltas)

## 6. Integration and testing

- [x] 6.1 Verify toggle persistence: set mode on Compare page, navigate to model page, confirm same mode is active
- [x] 6.2 Verify all three modes render correct fixture card sets with correct scores
- [x] 6.3 Verify filters (benchmark/difficulty/tag) work correctly in all three modes
- [x] 6.4 Verify "Both" card shows "—" for fixtures missing in one mode
- [x] 6.5 Verify toggle is hidden for models with no JSON variant
- [x] 6.6 Verify header stats switch correctly in all three modes
- [x] 6.7 Verify reliability summary refetches when toggle changes
- [x] 6.8 Verify reasoning level tab links preserve query params (existing behavior) and that output mode persists via localStorage (not URL)