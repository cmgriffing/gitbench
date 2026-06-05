## 1. Fixture Contracts

- [ ] 1.1 Add structured-output contract fields to fixture loading/types with backward-compatible defaults.
- [ ] 1.2 Define contract templates for each benchmark/scoring family, including commit messages, git commands, branch lists, commit selections, numeric counts, hashes, stash refs, and resolved file content.
- [ ] 1.3 Populate or derive concrete structured-output contracts for all 204 fixtures.
- [ ] 1.4 Add fixture validation that fails when any fixture lacks a contract, has invalid JSON Schema, permits undeclared object properties, or has inconsistent required fields.
- [ ] 1.5 Add canonicalization utilities that render structured payload fields back into scorer-compatible text.
- [ ] 1.6 Add tests proving each fixture's expected answer can be represented by its structured schema and canonicalized back to the expected scorer text.

## 2. Harness and Provider Support

- [ ] 2.1 Add `output_mode` configuration to the runner and CLI with `text` as the default and `json_schema` as the structured mode.
- [ ] 2.2 Pass fixture structured-output contracts from the runner to model adapters only for JSON-schema mode.
- [ ] 2.3 Implement OpenAI-compatible structured-output request serialization.
- [ ] 2.4 Implement OpenRouter-compatible structured-output forwarding without breaking existing reasoning forwarding.
- [ ] 2.5 Implement Ollama structured-output request serialization through native schema format support.
- [ ] 2.6 Normalize structured provider responses into canonical text, raw structured output, parsed payload, output mode, usage, transcript, and API timing.
- [ ] 2.7 Record structured parse and validation failures as failed fixture scores with useful errors.
- [ ] 2.8 Add unit tests for adapter request shapes, response normalization, parse failures, and unsupported-provider behavior.

## 3. Result Schema and Aggregation

- [ ] 3.1 Extend `Score` serialization with `output_mode`, raw structured output, parsed structured payload, and structured-output error fields.
- [ ] 3.2 Extend run envelopes with top-level `output_mode` and default missing historical values to `text`.
- [ ] 3.3 Update result deduplication to include `output_mode`.
- [ ] 3.4 Update result doctoring and rerun replacement logic to preserve and match output mode.
- [ ] 3.5 Update `aggregate_runs()` so text and JSON-schema runs for the same model remain separate variants while preserving provider/base-model/reasoning grouping.
- [ ] 3.6 Add aggregation tests for same model plus same benchmark in both output modes.

## 4. Report Data and APIs

- [ ] 4.1 Extend aggregate JSON types and generated `results.json` with output-mode-aware variants and structured-output fixture metadata.
- [ ] 4.2 Update SQLite schema primary keys/indexes to distinguish model/output-mode variants.
- [ ] 4.3 Update Python SQLite writer for output mode and structured-output payload columns.
- [ ] 4.4 Update JavaScript SQLite builder for output mode and structured-output payload columns.
- [ ] 4.5 Update report-store interfaces and Node SQLite queries to expose output mode and filter by mode where applicable.
- [ ] 4.6 Update API route query validation to accept valid `output_mode` filters and reject invalid values.
- [ ] 4.7 Add report DB and API tests covering text defaults, JSON-schema rows, compact omissions, and fixture-detail structured payloads.

## 5. Web UI

- [ ] 5.1 Extend frontend data types and model grouping helpers with output-mode variants.
- [ ] 5.2 Add an output-mode control next to model selectors with Text, JSON, and Both options.
- [ ] 5.3 Synchronize output-mode state across charts without encoding mode into model group IDs.
- [ ] 5.4 Update overview, benchmark, compare, and chart components to filter or expand by selected output modes.
- [ ] 5.5 Add model detail text-vs-structured comparison with aggregate delta, benchmark deltas, agreement counts, and changed fixture links.
- [ ] 5.6 Update fixture output cards to show structured payload fields and structured-output errors for JSON-schema results.
- [ ] 5.7 Update history to display output mode and compute deltas against prior runs with matching output mode.
- [ ] 5.8 Add focused component/page tests or API-backed smoke tests for output-mode selection and model detail comparison.

## 6. Verification

- [ ] 6.1 Run Python unit tests for fixture validation, runner, model adapters, scoring, result doctoring, rendering, and CLI behavior.
- [ ] 6.2 Run web API/report-store tests with `pnpm`.
- [ ] 6.3 Build or smoke-test the web report with text-only historical data to verify backward compatibility.
- [ ] 6.4 Generate a small text-vs-JSON-schema mock result set and verify report pages expose both modes separately.
- [ ] 6.5 Run OpenSpec validation for `compare-structured-output-modes`.
