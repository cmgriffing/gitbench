# fixture-structured-output Specification

## Purpose
Defines structured-output contracts for fixtures, enabling schema-enforced JSON runs with canonical text rendering for scoring.

## Requirements

### Requirement: Fixtures define structured-output contracts
Every fixture SHALL resolve to a strict structured-output contract for schema-enforced JSON runs. The contract SHALL include a JSON Schema object, a primary field or path, canonical text rendering instructions, and display metadata. The schema SHALL set `additionalProperties` to false for every object shape sent to a provider.

#### Scenario: Commit fixture uses semantic field
- **WHEN** a commit-message fixture is loaded for structured output
- **THEN** its contract exposes a string field named `commit`
- **AND** canonicalization renders the `commit` value as the scorer text

#### Scenario: Command fixture uses command fields
- **WHEN** a command-producing fixture is loaded for structured output
- **THEN** its contract exposes either `command` for one command or `commands` for multiple commands
- **AND** canonicalization renders the command field as the same command text shape used by the existing scorer

#### Scenario: List fixture uses array field
- **WHEN** a fixture expects a list of branches, commits, filenames, or similar items
- **THEN** its contract exposes a named array field for those items
- **AND** canonicalization renders the array using the fixture's expected line or list format

### Requirement: Structured-output contracts are validated for all fixtures
GitBench SHALL provide a validation path that checks every fixture has a usable structured-output contract before any all-fixture structured run is performed.

#### Scenario: Missing contract blocks validation
- **WHEN** the fixture validation path checks a fixture with no structured-output contract
- **THEN** validation fails and identifies the benchmark and fixture id

#### Scenario: Invalid schema blocks validation
- **WHEN** a fixture contract has an invalid JSON Schema, missing required property definition, or object schema that allows undeclared additional properties
- **THEN** validation fails and identifies the contract problem

#### Scenario: Canonical expected answer is representable
- **WHEN** validation checks a fixture contract
- **THEN** the fixture's expected answer can be represented as a structured payload and canonicalized back into scorer-compatible text

### Requirement: Structured responses canonicalize before scoring
For schema-enforced JSON runs, GitBench SHALL parse the model response, validate it against the fixture contract, render canonical scorer text from the declared field or path, and pass that canonical text to the existing benchmark scorer.

#### Scenario: Valid structured payload is scored through canonical text
- **WHEN** a structured response contains a valid payload for the fixture contract
- **THEN** `model_output` is set to the canonical text rendered from the structured payload
- **AND** the existing scorer receives that canonical text

#### Scenario: Parse failure is recorded as fixture failure
- **WHEN** a structured response cannot be parsed or validated against the fixture contract
- **THEN** the fixture result fails
- **AND** the result records a structured-output error without invoking a different scoring mode

### Requirement: Raw structured data is preserved
Structured-output fixture results SHALL preserve the raw provider output, parsed structured payload when available, and structured-output error details when parsing or validation fails.

#### Scenario: Parsed payload stored
- **WHEN** a structured response parses and validates successfully
- **THEN** the score payload includes the parsed structured payload
- **AND** the score payload includes the canonical `model_output`

#### Scenario: Invalid payload stored for debugging
- **WHEN** a structured response is invalid
- **THEN** the score payload includes the raw structured output where available
- **AND** the score payload includes a structured-output error message

### Requirement: Model adapters support provider-neutral structured output requests
The runner SHALL pass a provider-neutral structured-output contract to model adapters. Each adapter SHALL translate the contract to the provider's supported structured-output request shape or fail early with a clear unsupported-provider error.

#### Scenario: OpenAI-compatible structured request
- **WHEN** an OpenAI-compatible adapter receives `output_mode=json_schema`
- **THEN** it sends the fixture JSON Schema using the provider's structured-output response format

#### Scenario: Ollama structured request
- **WHEN** an Ollama adapter receives `output_mode=json_schema`
- **THEN** it sends the fixture JSON Schema using Ollama's native structured-output format support

#### Scenario: Unsupported structured output
- **WHEN** a provider adapter cannot support schema-enforced output
- **THEN** the run fails before fixture execution with a clear unsupported structured-output message
