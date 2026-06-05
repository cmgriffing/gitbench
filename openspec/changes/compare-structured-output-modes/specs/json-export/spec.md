## ADDED Requirements

### Requirement: JSON export preserves output mode
The aggregated report JSON SHALL include `output_mode` for every model variant, run metadata entry, benchmark summary, and fixture result. Historical result payloads that omit `output_mode` SHALL be treated as `text`.

#### Scenario: Text mode default for historical runs
- **WHEN** `aggregate_runs()` reads a historical run envelope without `output_mode`
- **THEN** the aggregated JSON represents that run as `output_mode: "text"`

#### Scenario: Structured run remains separate
- **WHEN** `aggregate_runs()` reads a text run and a JSON-schema run for the same model and benchmark
- **THEN** the aggregated JSON preserves both result variants without merging their fixture counts or pass rates

### Requirement: JSON export includes structured-output result metadata
Fixture results in aggregated JSON SHALL include structured-output metadata when available, including raw structured output, parsed payload, and structured-output error details.

#### Scenario: Valid structured result exported
- **WHEN** a structured fixture result has a parsed payload
- **THEN** the aggregated fixture result includes the parsed structured payload and canonical `model_output`

#### Scenario: Invalid structured result exported
- **WHEN** a structured fixture result has a structured-output error
- **THEN** the aggregated fixture result includes the structured-output error

### Requirement: JSON export exposes output-mode-aware model grouping
The aggregated JSON SHALL preserve provider/base-model/reasoning grouping while exposing output-mode variants for each effort that has text or JSON-schema results.

#### Scenario: Base model group contains mode variants
- **WHEN** a base model has `high` reasoning results in both text and JSON-schema modes
- **THEN** the corresponding base model group exposes both variants for the `high` effort
- **AND** each variant has its own pass rate and total cost
