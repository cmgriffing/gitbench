## ADDED Requirements

### Requirement: Report database stores output mode
The report database SHALL store `output_mode` for runs, model summaries, runtime summaries, benchmark summaries, and fixture result rows. Database access paths SHALL distinguish text and JSON-schema result variants for the same model.

#### Scenario: Result rows include output mode
- **WHEN** the report database is generated from aggregate data containing `output_mode=json_schema`
- **THEN** the corresponding fixture result rows store `json_schema` as their output mode

#### Scenario: Summary rows do not merge modes
- **WHEN** text and JSON-schema results exist for the same model
- **THEN** summary and benchmark rows keep separate aggregates for each output mode

### Requirement: Report APIs expose output mode filters
Report APIs SHALL expose output mode on returned model, run, benchmark, and fixture result payloads. APIs that return result rows SHALL accept an optional `output_mode` filter where mode filtering is meaningful.

#### Scenario: Model results filtered by output mode
- **WHEN** a client requests model results with `output_mode=json_schema`
- **THEN** only JSON-schema fixture results are returned for that model

#### Scenario: Fixture detail returns all modes
- **WHEN** a client requests fixture detail for a fixture that has text and JSON-schema outputs
- **THEN** the response includes both outputs and identifies each output's mode

#### Scenario: Unsupported output mode is rejected
- **WHEN** a client requests a report API with an unsupported `output_mode` value
- **THEN** the API returns a 400 response with a clear error

### Requirement: Report database stores structured-output payload fields
The report database SHALL store structured-output raw response text, parsed payload JSON, and structured-output error text for fixture results where those values exist.

#### Scenario: Structured payload is queryable
- **WHEN** a fixture result contains a parsed structured payload
- **THEN** fixture detail API responses can include that payload for debugging and display

#### Scenario: Compact endpoints omit bulky structured fields
- **WHEN** a summary, benchmark, or compact model-results endpoint returns fixture result rows
- **THEN** bulky raw structured output and full parsed payload data are omitted unless the endpoint is explicitly fixture-detail scoped
