## ADDED Requirements

### Requirement: Model selector is a searchable dropdown
The ModelSelector component SHALL render as a Popover-triggered Command menu instead of a flat row of pill checkboxes. The trigger SHALL display the number of selected models (e.g., "3 selected") or the names of selected models when few are chosen. Clicking the trigger SHALL open a dropdown containing a search input, a selectable list of all available models, and Select all / Clear all actions.

#### Scenario: Trigger shows selection count
- **WHEN** 3 models are selected
- **THEN** the trigger button displays "3 selected"

#### Scenario: Trigger shows model names when few selected
- **WHEN** 1 or 2 models are selected
- **THEN** the trigger button displays the model names (e.g., "gpt-4o, claude-sonnet")

#### Scenario: Trigger shows placeholder when nothing selected
- **WHEN** no models are selected
- **THEN** the trigger button displays "Select models..."

### Requirement: Search filters the flat model list
When the user types in the search input, the model list SHALL filter to entries whose `model.name` contains the search text (case-insensitive substring match). Filtering SHALL be immediate (no debounce). The list SHALL be flat — no grouping by `baseModel`.

#### Scenario: Search narrows results
- **WHEN** user types "gpt" in the search input
- **THEN** only models whose name contains "gpt" (case-insensitive) are shown (e.g., "gpt-4o", "gpt-4o#high", "gpt-4o#low")

#### Scenario: Search with no matches shows empty state
- **WHEN** user types a string matching no model names
- **THEN** the dropdown shows "No models found"

#### Scenario: Clearing search restores full list
- **WHEN** user clears the search input
- **THEN** all models are shown again

### Requirement: Models are selectable by checkbox
Each model entry in the list SHALL display a checkbox indicating selection state. Clicking an entry SHALL toggle its selection. The model pass rate (from `model_summaries`) SHALL be displayed next to each entry as contextual information.

#### Scenario: Toggle a model on
- **WHEN** user clicks an unselected model entry
- **THEN** its checkbox fills and the model is added to the selected set

#### Scenario: Toggle a model off
- **WHEN** user clicks a currently-selected model entry
- **THEN** its checkbox clears and the model is removed from the selected set

#### Scenario: Pass rate shown per entry
- **WHEN** the model list is displayed
- **THEN** each entry shows the model's overall pass rate (e.g., "92.5%") next to the name

### Requirement: Bulk actions are available
The dropdown SHALL include "Select all" and "Clear all" buttons at the top of the list, above the search input. "Select all" SHALL select every model in the current filtered view. "Clear all" SHALL deselect everything.

#### Scenario: Select all on filtered results
- **WHEN** user searches "gpt" (showing 3 models) and clicks "Select all"
- **THEN** only the 3 filtered models are selected; other models remain unselected

#### Scenario: Clear all
- **WHEN** user clicks "Clear all"
- **THEN** all models are deselected, trigger shows "Select models..."

### Requirement: Selection changes notify parent
When the selected set changes (via toggle, Select all, or Clear all), the component SHALL call the `onChange` callback with the updated array of selected model names. The callback SHALL be debounced — multiple rapid toggles within the same event loop tick SHALL result in a single callback.

#### Scenario: onChange fires after selection change
- **WHEN** user toggles a model on
- **THEN** `onChange(selectedNames)` is called with the updated array

#### Scenario: onChange fires once for Select all
- **WHEN** user clicks "Select all" on 50 models
- **THEN** `onChange` is called exactly once with all 50 names, not 50 separate calls

### Requirement: Initial selection is respected
The component SHALL accept an `initialSelected` prop (array of model names) and pre-select those models on mount. If `initialSelected` is empty or undefined, all models SHALL be selected by default.

#### Scenario: Pre-selection from URL parameter
- **WHEN** ComparePage mounts with `?with=gpt-4o`
- **THEN** "gpt-4o" is pre-selected in the dropdown

#### Scenario: Default all-selected when no initial value
- **WHEN** the component mounts with no `initialSelected` prop
- **THEN** all available models are selected
