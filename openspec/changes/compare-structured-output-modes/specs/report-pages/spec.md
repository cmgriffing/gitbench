## ADDED Requirements

### Requirement: Report pages support output-mode selection
Report pages with model selection SHALL provide an output-mode control that lets users view text results, JSON-schema results, or both when both modes exist in the report data.

#### Scenario: Output mode defaults to text
- **WHEN** a report page loads and no output mode is selected
- **THEN** text-mode results are shown by default

#### Scenario: Both modes expand selected models
- **WHEN** the user selects both output modes
- **THEN** charts and tables show separate text and JSON-schema variants for each selected model effort

### Requirement: Model detail page compares text and structured modes
The model level detail page SHALL show an output-mode comparison section when the current provider/base-model/reasoning level has both text and JSON-schema results.

#### Scenario: Comparison section shows aggregate delta
- **WHEN** the current model effort has both text and JSON-schema results
- **THEN** the page shows the pass-rate delta between JSON-schema and text modes
- **AND** it shows gained, lost, unchanged-pass, and unchanged-fail fixture counts

#### Scenario: Comparison section shows benchmark deltas
- **WHEN** both output modes have benchmark summary data
- **THEN** the page shows per-benchmark pass-rate deltas sorted by absolute delta

#### Scenario: Comparison section links fixture changes
- **WHEN** a fixture pass/fail status differs between text and JSON-schema modes
- **THEN** the comparison table includes a link to that fixture detail page

### Requirement: Fixture detail page displays structured fields
The fixture detail page SHALL display structured-output payload data with meaningful field labels when an output came from JSON-schema mode, while still showing canonical scorer text.

#### Scenario: Structured output card shows canonical and structured data
- **WHEN** a fixture output has a parsed structured payload
- **THEN** the output card shows the canonical scorer text and the structured field payload

#### Scenario: Structured error is visible
- **WHEN** a fixture output has a structured-output parse or validation error
- **THEN** the output card shows the structured-output error alongside the normal pass/fail state

### Requirement: History page distinguishes output modes
Run history SHALL identify the output mode for each run and SHALL compare deltas only against prior runs with the same model identity and output mode unless the user explicitly selects a cross-mode comparison.

#### Scenario: Run log shows mode
- **WHEN** the history table renders a JSON-schema run
- **THEN** the row identifies the run as JSON-schema mode

#### Scenario: Delta uses matching mode
- **WHEN** computing the previous-run delta for a text-mode run
- **THEN** only prior text-mode runs for the same model are considered
