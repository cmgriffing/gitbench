## ADDED Requirements

### Requirement: Dashboard page displays model summary cards
The Dashboard page (`index.astro`) SHALL render summary cards for each model showing the model name, overall pass rate percentage, and fixture count (passed/total). Cards SHALL be color-coded by pass rate threshold: green (≥80%), yellow (50-79%), red (<50%). Each card SHALL link to the corresponding Model Detail page.

#### Scenario: Dashboard renders model cards
- **WHEN** navigating to `/`
- **THEN** a summary card is displayed for each model in the dataset

#### Scenario: High pass rate card is green
- **WHEN** a model has ≥80% pass rate
- **THEN** its card uses the green/pass color treatment

#### Scenario: Clicking a model card navigates to model detail
- **WHEN** a user clicks a model summary card
- **THEN** the browser navigates to `/models/<encoded-model-name>`

### Requirement: Dashboard includes overview charts
The Dashboard SHALL include React island charts: an overall pass rate bar chart, a pass-by-difficulty stacked bar chart, and an interactive benchmark × model heatmap. Charts SHALL be accompanied by a shared `ModelSelector` island.

#### Scenario: Pass rate bar chart renders
- **WHEN** the Dashboard loads and React hydrates
- **THEN** a horizontal bar chart displays pass rate per selected model

#### Scenario: Heatmap renders with model and benchmark axes
- **WHEN** the Dashboard loads and React hydrates
- **THEN** a heatmap displays benchmarks as rows, selected models as columns, with cells colored by pass rate

#### Scenario: Clicking a heatmap cell navigates
- **WHEN** a user clicks a cell in the heatmap
- **THEN** the browser navigates to the corresponding Benchmark Detail page

### Requirement: Model Detail page shows model statistics and fixture gallery
The Model Detail page (`models/[model].astro`) SHALL display the model name, profile, run count, overall pass rate, and average similarity. It SHALL render a fixture gallery as static Astro cards — one card per fixture result — showing fixture ID, benchmark name, pass/fail status, and similarity percentage. It SHALL include a React `FilterBar` island for filtering cards by benchmark, difficulty, and tags.

#### Scenario: Model Detail renders fixture cards
- **WHEN** navigating to `/models/gpt-4o%23high`
- **THEN** fixture cards are displayed for every fixture result belonging to that model

#### Scenario: Filter bar hides non-matching cards
- **WHEN** user selects difficulty "hard" in the filter bar
- **THEN** only fixture cards with difficulty "hard" remain visible; others are hidden via CSS

#### Scenario: Clicking a fixture card navigates
- **WHEN** a user clicks a fixture card
- **THEN** the browser navigates to `/fixtures/<fixture-id>`

### Requirement: Model Detail page includes "Compare" button
The Model Detail page SHALL include a "Compare →" button that navigates to `/compare?with=<encoded-model-name>`, pre-selecting the current model.

#### Scenario: Compare button navigates to Compare page
- **WHEN** a user clicks "Compare →" on `/models/gpt-4o%23high`
- **THEN** the browser navigates to `/compare?with=gpt-4o%23high` with that model pre-selected

### Requirement: Model Detail page shows reasoning level comparison when applicable
When a base model has been run at multiple reasoning levels, the Model Detail page SHALL display a reasoning level comparison section showing the pass rate delta per benchmark between levels, sorted by delta magnitude.

#### Scenario: Reasoning comparison renders when multiple levels exist
- **WHEN** navigating to a model detail page for a base model with runs at `high`, `medium`, and `low`
- **THEN** a comparison table or chart shows per-benchmark pass rates for each reasoning level

#### Scenario: No reasoning comparison for single-level models
- **WHEN** navigating to a model detail page for a model with only one reasoning level
- **THEN** no reasoning comparison section is displayed

### Requirement: Benchmark Detail page shows leaderboard and per-fixture comparison
The Benchmark Detail page (`benchmarks/[name].astro`) SHALL render the benchmark description, a model leaderboard bar chart (React island), a per-fixture comparison table showing pass/fail and similarity for each selected model, and a tag breakdown chart.

#### Scenario: Leaderboard shows all selected models
- **WHEN** navigating to `/benchmarks/commit_messages`
- **THEN** a bar chart displays pass rate for each selected model on this benchmark

#### Scenario: Per-fixture table shows cross-model results
- **WHEN** navigating to `/benchmarks/commit_messages`
- **THEN** a table displays each fixture in the benchmark with columns for each selected model's pass/fail and similarity

#### Scenario: Clicking a fixture row navigates
- **WHEN** a user clicks a fixture row in the comparison table
- **THEN** the browser navigates to `/fixtures/<fixture-id>`

### Requirement: Fixture Detail page shows full prompt, expected, and all model outputs
The Fixture Detail page (`fixtures/[fixture].astro`) SHALL render the fixture metadata (id, description, purpose, difficulty, tags), the full prompt text in a monospace block, the full expected text in a monospace block, and all model outputs as static `ModelOutputCard` components showing model name, pass/fail badge, similarity score, and full output text. Each block SHALL include a copy-to-clipboard button.

#### Scenario: Full prompt is displayed in monospace
- **WHEN** navigating to `/fixtures/f001`
- **THEN** the complete prompt text is displayed in a monospace block with a copy button

#### Scenario: All model outputs are displayed
- **WHEN** navigating to `/fixtures/f001`
- **THEN** a card is rendered for each model that ran this fixture, showing the model name, similarity, pass/fail, and full output

#### Scenario: Copy button copies text to clipboard
- **WHEN** a user clicks the copy button on the prompt block
- **THEN** the full prompt text is copied to the system clipboard

### Requirement: Explore page provides tag-based fixture search
The Explore page (`explore.astro`) SHALL render a tag cloud showing all tags with fixture counts, and a React island for filter bar and filtered results. Selecting tags or difficulty levels SHALL filter the fixture list to show matching fixtures with per-model pass/fail sparkline bars.

#### Scenario: Tag cloud displays all tags
- **WHEN** navigating to `/explore`
- **THEN** all tags from the dataset are displayed with fixture counts

#### Scenario: Clicking a tag filters results
- **WHEN** a user clicks a tag in the tag cloud
- **THEN** the filtered results list shows only fixtures matching that tag

#### Scenario: Multiple filters combine with AND logic
- **WHEN** a user selects tag "rename" and difficulty "medium"
- **THEN** only fixtures matching BOTH criteria are displayed

### Requirement: Compare page enables multi-model analysis
The Compare page (`compare.astro`) SHALL be a React island component that provides: a multi-select model picker at the top, an overall pass rate comparison bar chart, a per-benchmark grouped comparison chart, a head-to-head scatter plot for two chosen models, an agreement matrix for the same two models, and a per-fixture detail table across all selected models.

#### Scenario: Model selection updates all comparison sections
- **WHEN** a user adds or removes models in the Compare page selector
- **THEN** all comparison sections (overall, by benchmark, head-to-head, per-fixture) update to reflect the new selection

#### Scenario: Head-to-head scatter plot renders per-fixture dots
- **WHEN** two models are selected for head-to-head comparison
- **THEN** a scatter plot displays one dot per fixture, with X = model A similarity, Y = model B similarity

#### Scenario: Agreement matrix shows pass/fail overlap
- **WHEN** two models are selected for head-to-head comparison
- **THEN** a 2×2 matrix shows counts of: both pass, both fail, A-only pass, B-only pass

#### Scenario: Pre-selection from query parameter
- **WHEN** navigating to `/compare?with=gpt-4o%23high`
- **THEN** `gpt-4o#high` is pre-selected in the model picker

### Requirement: History page shows run history and time series
The History page (`history.astro`) SHALL render a static run log table showing timestamp, model, pass rate, suite version, and delta from previous run. It SHALL include a React island time series chart showing pass rate over time per selected model. Expanding a run row SHALL show the specific fixtures that regressed or improved compared to the previous run of the same model.

#### Scenario: Run log table is rendered statically
- **WHEN** navigating to `/history`
- **THEN** a table displays all runs sorted by timestamp descending, without requiring JavaScript

#### Scenario: Time series chart shows pass rate over calendar time
- **WHEN** the History page loads and React hydrates
- **THEN** a line chart displays pass rate over time for each selected model

#### Scenario: Expanding a run row shows fixture deltas
- **WHEN** a user clicks to expand a run row
- **THEN** the expanded area lists fixtures whose pass status or similarity changed significantly from the previous run
