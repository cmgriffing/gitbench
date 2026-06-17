## MODIFIED Requirements

### Requirement: Model level drill-down page shows fixture gallery
The model level page (`/models/[provider]/[model]/[level]/`) SHALL display: the full model identity (provider icon, base model, level), a reasoning level tab bar linking to sibling levels of the same base model and sorted by effort order, a summary stats area (pass rate, total cost, input/output token counts), a "Compare" button linking to `/compare?with=<encoded-full-model-name>`, and a fixture gallery with filter controls (benchmark, difficulty, tag). Fixture gallery filter controls SHALL be implemented using plain JavaScript (no TypeScript syntax) so they execute correctly in the browser. Difficulty values in the filter dropdown SHALL be sorted by difficulty order (trivial, easy, medium, hard, expert), not alphabetically. The token summary in the header SHALL display separate input and output token counts (e.g., "15.2K in / 48.7K out tokens") rather than a single total.

The page SHALL include a page-wide output mode toggle (Text, JSON, Both) in the fixture gallery filter bar. This toggle SHALL control the header stats, reliability summary, and fixture gallery. The toggle SHALL use the same `gitbench-output-mode` localStorage key used by the rest of the site, so output mode preference persists across page navigations. When the model has no JSON-schema variant, the toggle SHALL be hidden and the page SHALL display text-mode results only (current behavior).

The fixture gallery SHALL pre-render three card sets at build time: text-mode cards, JSON-schema cards, and "both" compact cards. The toggle SHALL control which card set is visible via client-side visibility toggling. Existing filter controls (benchmark, difficulty, tag) SHALL apply to whichever card set is visible.

In single-mode view (Text or JSON), fixture cards SHALL display fixture ID, benchmark, pass/fail status, similarity percentage, and token counts (current `FixtureCard` behavior). In "Both" view, fixture cards SHALL display fixture ID, benchmark, and stacked text and JSON scores (e.g., "T 87% ✓" / "J 91% ✓") without token details. When a fixture exists in one mode but not the other, the missing mode SHALL show "—" for its score.

The header stats area SHALL pre-render both text and JSON summary blocks at build time. In single-mode view, the matching stats block SHALL be visible. In "Both" view, both stat blocks SHALL be shown stacked (text first, then JSON). The `ModelReliabilitySummary` React island SHALL read the persisted output mode from localStorage for its initial fetch and SHALL listen for the `output-mode-change` custom event to refetch when the toggle changes. In "Both" mode, the reliability summary SHALL show text-mode results (the "Text vs JSON Comparison" section below already covers cross-mode deltas).

The "Text vs JSON Schema Comparison" section SHALL remain unchanged — it is inherently about both modes and continues to render only when both variants exist.

#### Scenario: Tabs link to sibling levels sorted by effort order
- **WHEN** viewing `/models/anthropic/claude-opus-4.7/low/`
- **THEN** a tab bar shows sibling levels in effort order [default, low, medium, high, xhigh, max] with "low" visually active; clicking "high" navigates to `/models/anthropic/claude-opus-4.7/high/`

#### Scenario: Fixture gallery filters work
- **WHEN** user selects benchmark "git_grep" in the filter bar
- **THEN** only fixture cards for git_grep remain visible

#### Scenario: Multiple filters combine with AND logic
- **WHEN** user selects benchmark "git_grep" and difficulty "medium"
- **THEN** only fixture cards matching BOTH benchmark "git_grep" AND difficulty "medium" remain visible

#### Scenario: Reset button clears all filters
- **WHEN** user clicks the Reset button after applying filters
- **THEN** all filter dropdowns reset to "All" and all fixture cards become visible

#### Scenario: Difficulty dropdown sorted by difficulty
- **WHEN** the page renders with fixtures of difficulties "hard", "easy", "medium"
- **THEN** the difficulty filter dropdown options appear in order: easy, medium, hard

#### Scenario: Token summary shows input/output split
- **WHEN** a model level has fixtures totaling 15,200 input tokens and 48,700 output tokens
- **THEN** the header summary displays "15.2K in / 48.7K out tokens" (or similar formatting)

#### Scenario: Token summary with zero tokens
- **WHEN** a model level has no token data (all null)
- **THEN** no token summary is displayed

#### Scenario: Compare button navigates correctly
- **WHEN** user clicks "Compare" on the page for `anthropic/claude-opus-4.7:low`
- **THEN** the browser navigates to `/compare?with=anthropic%2Fclaude-opus-4.7%3Alow`

#### Scenario: Output mode toggle defaults to text
- **WHEN** the page loads with no persisted output mode in localStorage
- **THEN** text-mode fixture cards are visible, JSON and both card sets are hidden, and the toggle shows "Text" as active

#### Scenario: Output mode toggle reads persisted preference
- **WHEN** the page loads and localStorage contains `gitbench-output-mode` = `json_schema`
- **THEN** JSON fixture cards are visible and the toggle shows "JSON" as active

#### Scenario: Output mode toggle writes to localStorage
- **WHEN** user clicks "Both" on the toggle
- **THEN** `gitbench-output-mode` is set to `both` in localStorage and compact both-mode cards are visible

#### Scenario: Toggle hidden when no JSON variant exists
- **WHEN** the model has no JSON-schema variant (`jsonModelName` is null)
- **THEN** the output mode toggle is not rendered and the gallery shows text cards only

#### Scenario: Both-mode card shows stacked scores
- **WHEN** the toggle is set to "Both" and fixture f001 has text similarity 87% (pass) and JSON similarity 91% (pass)
- **THEN** the card displays "T 87% ✓" and "J 91% ✓" stacked, without token details

#### Scenario: Both-mode card shows dash for missing mode
- **WHEN** the toggle is set to "Both" and fixture f001 has text results but no JSON results
- **THEN** the card displays "T 87% ✓" and "J —"

#### Scenario: Header stats toggle between modes
- **WHEN** the user switches the toggle from "Text" to "JSON"
- **THEN** the header stats area swaps from showing text pass rate/tokens/cost to showing JSON pass rate/tokens/cost

#### Scenario: Header stats show both stacked
- **WHEN** the toggle is set to "Both"
- **THEN** the header stats area shows text stats block first, then JSON stats block below

#### Scenario: Reliability summary refetches on toggle change
- **WHEN** the user switches the toggle from "Text" to "JSON"
- **THEN** the `ModelReliabilitySummary` React island refetches from the API with `output_mode=json_schema`

#### Scenario: Reliability summary shows text in both mode
- **WHEN** the toggle is set to "Both"
- **THEN** the `ModelReliabilitySummary` shows text-mode reliability results (the comparison section below covers cross-mode deltas)

#### Scenario: Filters apply to visible card set
- **WHEN** the toggle is set to "JSON" and the user selects benchmark "merge_conflicts"
- **THEN** only JSON fixture cards for merge_conflicts remain visible