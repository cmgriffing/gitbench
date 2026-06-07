## ADDED Requirements

### Requirement: Transcripts preserve structured-output context
When a model call uses schema-enforced JSON output, the recorded transcript SHALL preserve enough structured-output context to debug the request and response, including the output mode and schema name or fixture contract identifier.

#### Scenario: Structured transcript includes mode metadata
- **WHEN** a model adapter records a transcript for a JSON-schema mode request
- **THEN** the transcript metadata identifies the output mode as `json_schema`

#### Scenario: Structured transcript preserves assistant payload
- **WHEN** a JSON-schema mode response is recorded
- **THEN** the assistant entry preserves the raw assistant content returned by the provider
- **AND** the score payload can be inspected to see the parsed structured payload or structured-output error
