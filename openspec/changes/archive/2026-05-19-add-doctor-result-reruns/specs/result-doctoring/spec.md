## ADDED Requirements

### Requirement: Doctor command repairs existing result files
GitBench SHALL provide a `doctor` CLI command that repairs existing results JSON files by selectively rerunning doctorable failed fixture entries and updating the result payload.

#### Scenario: Explicit result file is repaired
- **WHEN** the user runs `gitbench doctor path/to/results-v0.1.0.json`
- **THEN** GitBench scans that file for doctorable failed fixture entries, reruns only those entries, and updates that result file

#### Scenario: Original file is updated in place
- **WHEN** `gitbench doctor path/to/results-v0.1.0.json` completes successfully without an explicit output path
- **THEN** the original input file contains the repaired result payload

#### Scenario: Explicit output path is honored
- **WHEN** the user runs `gitbench doctor path/to/results.json --output path/to/fixed.json`
- **THEN** GitBench writes the repaired result payload to `path/to/fixed.json`

### Requirement: Doctor command can target default result files
The `doctor` command SHALL support a `--latest` option that selects all current JSON result files under `gitbench-results/`.

#### Scenario: Default result files exist
- **WHEN** the user runs `gitbench doctor --latest`
- **THEN** GitBench scans every JSON result file under `gitbench-results/` and doctors each file that contains doctorable failures

#### Scenario: No default result file exists
- **WHEN** the user runs `gitbench doctor --latest` and no JSON result file exists under `gitbench-results/`
- **THEN** GitBench fails with a clear error explaining that no result file was found

### Requirement: Dry-run reports doctor plan without rerunning fixtures
The `doctor` command SHALL support a dry-run mode that reports the doctor plan without calling model providers or writing results.

#### Scenario: Dry-run prints counts
- **WHEN** the user runs `gitbench doctor path/to/results.json --dry-run`
- **THEN** GitBench prints the number of doctorable failed fixture entries, affected models, and affected model/benchmark pairs

#### Scenario: Dry-run does not write output
- **WHEN** the user runs `gitbench doctor path/to/results.json --dry-run`
- **THEN** GitBench does not create or modify any results JSON file

### Requirement: Doctorability is determined by hardcoded legacy error patterns
GitBench SHALL treat a failed score as doctorable when its `error` field contains one of the hardcoded transient error patterns supported by the `doctor` command.

#### Scenario: Resource exhaustion is doctorable
- **WHEN** a score has `error` equal to `[Errno 24] Too many open files`
- **THEN** `gitbench doctor` includes that score in the rerun plan

#### Scenario: Model timeout is doctorable
- **WHEN** a score has an `error` containing `Model call timed out after`
- **THEN** `gitbench doctor` includes that score in the rerun plan

#### Scenario: Provider transient error is doctorable
- **WHEN** a score has an `error` containing `RateLimitError`, `APITimeoutError`, `APIConnectionError`, `InternalServerError`, `429`, `500`, `502`, `503`, or `504`
- **THEN** `gitbench doctor` includes that score in the rerun plan

#### Scenario: Scoring failure is not doctorable
- **WHEN** a score has an `error` containing failed assertions, expected/got mismatches, extra selected commit messages, or command-equivalence failures
- **THEN** `gitbench doctor` leaves that score unchanged by default

### Requirement: Doctor reruns only targeted fixtures
The `doctor` command SHALL rerun only the fixture IDs selected by the doctor plan for each affected model and benchmark.

#### Scenario: One fixture in a benchmark is doctorable
- **WHEN** a benchmark result contains twelve fixture scores and only fixture `f007` is doctorable
- **THEN** `gitbench doctor` reruns fixture `f007` for that model and benchmark
- **AND** the other eleven fixture scores remain unchanged

#### Scenario: Multiple fixtures in the same model benchmark are doctorable
- **WHEN** a model has multiple doctorable fixture errors for the same benchmark
- **THEN** `gitbench doctor` reruns those selected fixtures as a group for that model/benchmark pair

### Requirement: Doctor preserves result structure while recomputing summaries
After successful reruns, `gitbench doctor` SHALL preserve the input result file structure and recompute all affected summaries from the updated scores.

#### Scenario: Benchmark summary is recomputed
- **WHEN** a repaired fixture score replaces an error score
- **THEN** the containing benchmark result's `passed`, `errors`, and `pass_at_k` fields are recomputed from its scores

#### Scenario: Model profile and top-level summaries are recomputed
- **WHEN** a repaired result file contains model, profile, or top-level summary fields
- **THEN** GitBench recomputes those summaries from the updated benchmark results before writing output

#### Scenario: Existing schema is unchanged
- **WHEN** `gitbench doctor` writes a repaired result file
- **THEN** the output uses the same result schema fields as the input and does not require new error classification fields

### Requirement: Doctor uses current configuration to recreate model clients
The `doctor` command SHALL use the current GitBench configuration to resolve provider settings for each affected result model before rerunning fixtures.

#### Scenario: Profile and model can be resolved
- **WHEN** a doctorable result entry references a profile and model present in the current config
- **THEN** GitBench uses that config to create the model client for rerunning the selected fixture

#### Scenario: Profile or model cannot be resolved
- **WHEN** a doctorable result entry references a profile or model that cannot be resolved from current config
- **THEN** `gitbench doctor` fails before rerunning fixtures and reports the unresolved profile or model
