## MODIFIED Requirements

### Requirement: Benchmark Detail page shows leaderboard and per-fixture comparison
The Benchmark Detail page (`benchmarks/[name].astro`) SHALL render the benchmark description, a model leaderboard bar chart (React island) showing pass rates for this specific benchmark only, a per-fixture comparison table (`FixtureComparisonTable` React island) showing pass/fail and similarity for each selected model with its own synced `ModelSelector`, and a tag breakdown chart.

#### Scenario: Leaderboard shows per-benchmark pass rates for all selected models
- **WHEN** navigating to `/benchmarks/commit_messages`
- **THEN** the `PassRateBarChart` is rendered with `benchmarkName="commit_messages"` and displays pass rates computed only from the `commit_messages` fixture set, not the global 204-fixture average

#### Scenario: Per-fixture table uses synced model selection
- **WHEN** navigating to `/benchmarks/commit_messages` with model selection `["anthropic/claude-opus-4.7", "openai/gpt-4o"]`
- **THEN** the fixture comparison table shows only those model groups' efforts as columns

#### Scenario: Per-fixture table has its own ModelSelector
- **WHEN** viewing the per-fixture comparison section
- **THEN** a `ModelSelector` widget appears above the table; changing it updates the table columns and syncs across all other selectors on the site

#### Scenario: Clicking a fixture row navigates
- **WHEN** a user clicks a fixture row in the comparison table
- **THEN** the browser navigates to `/fixtures/<benchmark>/<fixture-id>`

#### Scenario: Fixture cells show similarity scores with pass/fail coloring
- **WHEN** a model passed a fixture with 100% similarity
- **THEN** the cell shows "100.0%" in a pass-colored badge

#### Scenario: Missing fixture results show dash
- **WHEN** a model has no result for a fixture
- **THEN** the cell displays "—" in dim text
