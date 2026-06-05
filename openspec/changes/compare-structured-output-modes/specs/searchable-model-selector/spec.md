## ADDED Requirements

### Requirement: Output mode selection is separate from model group selection
The model selection experience SHALL keep provider/base-model group selection separate from output-mode selection. Changing output mode SHALL NOT change the selected model group IDs stored by the searchable model selector.

#### Scenario: Switching output mode preserves selected models
- **WHEN** the user changes from text mode to JSON-schema mode
- **THEN** the selected provider/base-model groups remain unchanged

#### Scenario: Model selection persists independently
- **WHEN** selected model groups are persisted to localStorage
- **THEN** the persisted model group list does not encode output mode in model group IDs

### Requirement: Output mode state synchronizes across charts
Output mode selection SHALL synchronize across report components on the same page similarly to model selection, so charts and tables use the same selected output-mode state.

#### Scenario: Output mode change updates charts
- **WHEN** the user selects JSON-schema mode next to a model selector
- **THEN** other charts and tables on the page update to JSON-schema results

#### Scenario: Both mode exposes variants
- **WHEN** the user selects both output modes
- **THEN** model group expansion returns separate text and JSON-schema variants where available
