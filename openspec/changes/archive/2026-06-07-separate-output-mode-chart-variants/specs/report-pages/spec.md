## MODIFIED Requirements

### Requirement: Compare page enables multi-model analysis
The Compare page (`compare.astro`) SHALL be a React island component that provides: a multi-select model picker at the top, an overall pass rate comparison bar chart, a per-benchmark grouped comparison chart, a head-to-head scatter plot for two chosen models, an agreement matrix for the same two models, and a per-fixture detail table across all selected models. When `Both` output modes are selected, both bar charts SHALL pair text and JSON-schema results under canonical model-effort identities rather than presenting `__json_schema` variants as unrelated models. Text bars SHALL use each chart's solid base color and JSON bars SHALL use the same base color with reduced fill opacity and a visible outline. Both charts SHALL provide a mode-style legend and one pair-level tooltip from either sibling bar with separate `Text` and `JSON` sections.

#### Scenario: Model selection updates all comparison sections
- **WHEN** a user adds or removes models in the Compare page selector
- **THEN** all comparison sections (overall, by benchmark, head-to-head, per-fixture) update to reflect the new selection

#### Scenario: Overall chart pairs output modes by model effort
- **WHEN** `Both` is selected and a reasoning effort has text and JSON-schema pass-rate summaries
- **THEN** the overall chart renders one canonical model-effort label with adjacent text and JSON bars

#### Scenario: Overall pair shares one tooltip
- **WHEN** a user hovers or keyboard-focuses either sibling in the overall pass-rate chart
- **THEN** one tooltip shows separate `Text` and `JSON` pass-rate sections for that canonical model effort

#### Scenario: Overall chart sorts by mean pass rate in Both mode
- **WHEN** `Both` is selected and a model effort has both text and JSON pass rates
- **THEN** the overall chart sorts its canonical model-effort category by the mean of those two pass rates

#### Scenario: Per-benchmark chart pairs model series
- **WHEN** `Both` is selected
- **THEN** each benchmark category renders every canonical model effort's text and JSON bars consecutively with compact spacing inside the pair

#### Scenario: Per-benchmark pair shares one scoped tooltip
- **WHEN** a user hovers either output-mode bar for one model effort on a benchmark
- **THEN** one tooltip shows that benchmark and model effort with separate `Text` and `JSON` pass-rate sections
- **AND** the tooltip does not include unrelated selected models

#### Scenario: Compare legends hide storage suffixes
- **WHEN** `Both` is selected
- **THEN** model legends and labels use canonical model-effort identities without displaying the `__json_schema` suffix
- **AND** a separate mode legend explains the text and JSON bar treatments

#### Scenario: Missing mode remains explicit
- **WHEN** a model effort has only one output mode for an overall or per-benchmark value
- **THEN** the available bar remains grouped under the canonical identity and the shared tooltip labels the other mode `No data`

#### Scenario: Single mode renders one bar per model effort
- **WHEN** `Text` or `JSON` is selected
- **THEN** both Compare bar charts render only the selected mode without reserving an empty sibling slot

#### Scenario: Head-to-head scatter plot renders per-fixture dots
- **WHEN** two models are selected for head-to-head comparison
- **THEN** a scatter plot displays one dot per fixture, with X = model A similarity, Y = model B similarity

#### Scenario: Agreement matrix shows pass/fail overlap
- **WHEN** two models are selected for head-to-head comparison
- **THEN** a 2×2 matrix shows counts of: both pass, both fail, A-only pass, B-only pass

#### Scenario: Pre-selection from query parameter
- **WHEN** navigating to `/compare?with=gpt-4o%23high`
- **THEN** `gpt-4o#high` is pre-selected in the model picker
