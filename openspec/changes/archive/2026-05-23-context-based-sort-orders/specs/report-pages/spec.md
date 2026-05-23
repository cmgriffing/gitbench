## MODIFIED Requirements

### Requirement: Models index page groups by provider and base model
The Models index page (`/models`) SHALL render models grouped by provider, then by base model within each provider. Each provider section SHALL display the provider brand icon and provider name as a header. Within each provider section, base models SHALL be displayed as cards containing sub-cards for each reasoning level. Reasoning level sub-cards SHALL be sorted by reasoning effort order: default/none, low, medium, high, xhigh, max. Each level sub-card SHALL show: the level name, pass rate percentage (color-coded), and total cost in USD. Clicking a level sub-card SHALL navigate to `/models/<provider>/<base-model>/<level>/`.

#### Scenario: Models grouped by provider
- **WHEN** the Models page renders with models from anthropic and openai
- **THEN** two provider sections appear: "Anthropic" (with its icon) and "OpenAI" (with its icon)

#### Scenario: Reasoning levels as sub-cards under base model
- **WHEN** anthropic/claude-opus-4.7 has runs at low, medium, high, xhigh, and max
- **THEN** five level sub-cards appear inside the claude-opus-4.7 card, each showing its pass rate and total cost

#### Scenario: Reasoning levels sorted by effort order
- **WHEN** a base model has levels "high", "low", "medium", "default"
- **THEN** the sub-cards appear in order: default, low, medium, high

#### Scenario: Clicking a level sub-card navigates to drill-down
- **WHEN** a user clicks the "low" sub-card under claude-opus-4.7
- **THEN** the browser navigates to `/models/anthropic/claude-opus-4.7/low/`

### Requirement: Base model overview page shows level comparison
The base model overview page (`/models/[provider]/[model]/`) SHALL display the provider icon, provider name, and base model name as a header. Below, it SHALL render reasoning level cards sorted by effort order (default/none, low, medium, high, xhigh, max) showing pass rate and total cost for each level. Each card SHALL link to the level's fixture gallery page.

#### Scenario: Level cards displayed for base model
- **WHEN** navigating to `/models/anthropic/claude-opus-4.7/`
- **THEN** cards for low, medium, high, xhigh, and max are displayed with pass rates and costs, in ascending effort order

#### Scenario: Header shows provider and base model
- **WHEN** navigating to `/models/anthropic/claude-opus-4.7/`
- **THEN** the page heading includes the Anthropic icon and "Anthropic / claude-opus-4.7"

### Requirement: Model level drill-down page shows fixture gallery
The model level page (`/models/[provider]/[model]/[level]/`) SHALL display: the full model identity (provider icon, base model, level), a reasoning level tab bar linking to sibling levels of the same base model and sorted by effort order, a summary stats area (pass rate, total cost, input/output token counts), a "Compare" button linking to `/compare?with=<encoded-full-model-name>`, and a fixture gallery with filter controls (benchmark, difficulty, tag). Fixture gallery filter controls SHALL be implemented using plain JavaScript (no TypeScript syntax) so they execute correctly in the browser. Difficulty values in the filter dropdown SHALL be sorted by difficulty order (trivial, easy, medium, hard, expert), not alphabetically. The token summary in the header SHALL display separate input and output token counts (e.g., "15.2K in / 48.7K out tokens") rather than a single total.

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

### Requirement: Explore page provides tag-based fixture search
The Explore page (`explore.astro`) SHALL render a tag cloud showing all tags with fixture counts, and filter controls for tag, difficulty, and benchmark. Difficulty filter dropdown options SHALL be sorted by difficulty order (trivial, easy, medium, hard, expert), not alphabetically. Selecting tags or difficulty levels SHALL filter the fixture list to show matching fixtures.

#### Scenario: Tag cloud displays all tags
- **WHEN** navigating to `/explore`
- **THEN** all tags from the dataset are displayed with fixture counts

#### Scenario: Clicking a tag filters results
- **WHEN** a user clicks a tag in the tag cloud
- **THEN** the filtered results list shows only fixtures matching that tag

#### Scenario: Multiple filters combine with AND logic
- **WHEN** a user selects tag "rename" and difficulty "medium"
- **THEN** only fixtures matching BOTH criteria are displayed

#### Scenario: Difficulty dropdown sorted by difficulty order
- **WHEN** navigating to `/explore`
- **THEN** the difficulty filter dropdown options appear in order: trivial, easy, medium, hard, expert
