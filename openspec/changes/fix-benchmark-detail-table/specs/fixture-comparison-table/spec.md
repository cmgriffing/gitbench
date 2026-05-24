## ADDED Requirements

### Requirement: FixtureComparisonTable renders per-fixture comparison with synced ModelSelector
The `FixtureComparisonTable` React component SHALL render a data table where rows are fixtures from a single benchmark and columns show similarity scores for selected models. The component SHALL include a `ModelSelector` widget at the top that reads and writes the shared model selection (localStorage + `model-selection-changed` CustomEvent). The component SHALL accept a `benchmarkName` prop identifying which benchmark's fixtures to display.

#### Scenario: Table shows only fixtures for the specified benchmark
- **WHEN** `FixtureComparisonTable` renders with `benchmarkName="blame_forensics"`
- **THEN** the table rows are the 12 fixtures in `blame_forensics` from `fixture_index`

#### Scenario: Table shows only selected model columns
- **WHEN** model selection contains `anthropic/claude-opus-4.7` and `openai/gpt-4o`
- **THEN** only those two model groups' efforts appear as columns; unselected model groups are absent

#### Scenario: Selection syncs with other ModelSelectors
- **WHEN** the user changes selection in the table's `ModelSelector`
- **THEN** the `model-selection-changed` event fires, updating all other `ModelSelector` instances and charts on the page

#### Scenario: Table reads shared selection on mount
- **WHEN** the table mounts and localStorage has `["anthropic/claude-opus-4.7"]`
- **THEN** the table's `ModelSelector` shows that group selected and the table shows only that group's efforts

#### Scenario: Empty selection shows all model groups
- **WHEN** the table mounts and no prior selection exists (localStorage empty)
- **THEN** all model groups are selected by default

### Requirement: FixtureComparisonTable expands model groups to effort columns
The table SHALL expand each selected model group into individual effort columns. For a group with reasoning levels `none`, `low`, `medium`, `high`, those four columns SHALL appear under a grouped header showing the provider and base model name. Each effort column SHALL display the reasoning level as the column label.

#### Scenario: Model group header spans effort columns
- **WHEN** `anthropic/claude-opus-4.7` has efforts at `low`, `medium`, `high`
- **THEN** a header row shows "claude-opus-4.7" spanning three columns: "low", "medium", "high"

#### Scenario: Single-effort group has single column
- **WHEN** a model group has only one effort level `none`
- **THEN** that group occupies one column with "none" as the label

### Requirement: FixtureComparisonTable matches fixture results by bare fixture ID
The table SHALL look up fixture results using `fixture_index[fixtureKey].id` (the bare ID like `"f001"`), not the full fixture_index key (like `"blame_forensics/f001"`). The full key SHALL only be used to read `fixture_index` metadata. The bare ID SHALL be used for result matching and fixture detail links.

#### Scenario: Result matched by bare fixture ID
- **WHEN** iterating fixture `blame_forensics/f001` whose `fixture_index` entry has `id: "f001"`
- **THEN** the table looks up results via `results.find(r => r.fixture_id === "f001")`

#### Scenario: Fixture link uses bare fixture ID
- **WHEN** rendering a row for fixture `blame_forensics/f001`
- **THEN** the fixture link points to `/fixtures/blame_forensics/f001`

### Requirement: FixtureComparisonTable shows similarity and pass/fail in each cell
Each cell SHALL display the similarity percentage (rounded to one decimal) with pass/fail color coding. Passed fixtures (similarity ≥ threshold) SHALL use the pass color scheme; failed fixtures SHALL use the fail color scheme. Missing results (model did not run this fixture) SHALL display "—" in dim text.

#### Scenario: Passed fixture shows green badge
- **WHEN** a model's result for a fixture has `passed: true` and `similarity: 0.95`
- **THEN** the cell displays "95.0%" in pass-colored badge

#### Scenario: Failed fixture shows red badge
- **WHEN** a model's result for a fixture has `passed: false` and `similarity: 0.42`
- **THEN** the cell displays "42.0%" in fail-colored badge

#### Scenario: Missing result shows dash
- **WHEN** a model has no result entry for a given fixture
- **THEN** the cell displays "—" in dim, low-opacity text
