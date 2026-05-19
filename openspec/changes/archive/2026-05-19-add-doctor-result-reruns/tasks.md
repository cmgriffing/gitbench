## 1. Planning and Detection

- [x] 1.1 Add doctorable error pattern utilities with coverage for timeout, rate limit, server error, connection error, and `[Errno 24] Too many open files` legacy messages
- [x] 1.2 Add result-file scanning utilities that produce a rerun plan grouped by profile, model, benchmark, and fixture IDs
- [x] 1.3 Add default result discovery for all current `gitbench-results/**/*.json` files
- [x] 1.4 Add dry-run summary formatting for doctorable count, affected model count, affected model/benchmark pair count, and error-pattern breakdown

## 2. Selective Fixture Execution

- [x] 2.1 Add internal runner support for loading and executing selected fixture IDs within a benchmark
- [x] 2.2 Ensure selected fixture execution preserves normal setup, prompt formatting, scoring, duration, token, and cost behavior
- [x] 2.3 Ensure missing selected fixture IDs fail with a clear error before writing repaired output

## 3. Result Repair

- [x] 3.1 Add score replacement logic for combined result payloads with `profiles[].models[].results[].scores[]`
- [x] 3.2 Recompute benchmark `passed`, `errors`, `pass_at_k`, and timing totals after score replacement
- [x] 3.3 Recompute model, profile, and top-level summaries from updated benchmark results
- [x] 3.4 Preserve non-target scores and existing result structure without adding new schema fields
- [x] 3.5 Add default in-place result file updates

## 4. CLI Integration

- [x] 4.1 Add `gitbench doctor <result-file>` command wiring
- [x] 4.2 Add `gitbench doctor --latest` input selection
- [x] 4.3 Add `--dry-run` and ensure it performs no model calls or file writes
- [x] 4.4 Add `--output` and write repaired JSON to the requested path
- [x] 4.5 Resolve affected profile/model provider settings from current config and fail early when any target cannot be resolved

## 5. Verification

- [x] 5.1 Add unit tests for doctorable and non-doctorable error classification
- [x] 5.2 Add unit tests for rerun-plan grouping from a representative combined result payload
- [x] 5.3 Add unit tests for summary recomputation after score replacement
- [x] 5.4 Add CLI tests for explicit input file, `--latest`, `--dry-run`, and `--output`
- [x] 5.5 Add an integration-style test proving only targeted failed fixture IDs are rerun and non-target failures remain unchanged
- [x] 5.6 Run the focused test suite for CLI, runner, and result-doctoring behavior
