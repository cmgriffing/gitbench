## Context

GitBench currently runs complete benchmark/model sets and writes combined JSON results. When a fixture fails during execution, the runner records the exception as `Score.error`. The latest result file includes many legitimate scoring failures, plus transient failures such as `[Errno 24] Too many open files` and `Model call timed out after 30s`.

The first version of `doctor` needs to repair existing result files. It cannot depend on new fields such as `error_kind` or `doctorable`, and it should not change the result schema.

## Goals / Non-Goals

**Goals:**
- Provide `gitbench doctor` for selective repair of existing result JSON files.
- Support `--latest`, explicit input path, `--dry-run`, and `--output`.
- Detect doctorable failures from hardcoded legacy error patterns.
- Rerun only affected fixture IDs for the affected model/benchmark entries.
- Preserve all non-target scores byte-for-byte where practical.
- Recompute summaries after replacing repaired scores.
- Update result files in place by default.

**Non-Goals:**
- No result schema changes in this change.
- No broad rerun of all failed fixtures.
- No interactive review UI.
- No attempt to infer doctorability from every possible provider error message.
- No changes to report aggregation semantics beyond accepting repaired result files as normal input.

## Decisions

### Add a dedicated `doctor` command

`gitbench doctor` will own result repair semantics instead of overloading `gitbench run`.

Alternatives considered:
- `gitbench run --rerun-failed`: reuses the existing command, but mixes fresh-run and file-repair behavior.
- `gitbench verify --rerun`: implies validation rather than repair and no `verify` command currently exists.

### Use explicit doctorable error patterns

Doctorability will be determined by code-owned patterns against `score.error`. Initial patterns:
- `[Errno 24] Too many open files`
- `Model call timed out after`
- `RateLimitError`
- `APITimeoutError`
- `APIConnectionError`
- `InternalServerError`
- `429`
- `500`
- `502`
- `503`
- `504`

Everything else remains non-doctorable by default, including failed assertions, expected/got mismatches, extra selections, and command-equivalence failures.

Alternatives considered:
- Add `error_kind` and `doctorable` to new result files. This would be cleaner for future runs, but it does not help the existing result file and expands output behavior beyond the current scope.

### Patch the result payload

By default, doctor updates the input file in place. When `--output` is provided for a single explicit input file, doctor writes the repaired payload to that path instead.

The command will update the existing combined-result structure in place:
- locate each target score by profile/model/benchmark/fixture ID
- rerun the fixture
- replace the score object
- recompute enclosing benchmark/model/profile/top-level summaries

### Add internal selected-fixture execution

The runner needs a way to execute only selected fixture IDs for a benchmark. This can be an internal helper used by `doctor` rather than a public `gitbench run` option.

For each affected model/benchmark pair, doctor should run the benchmark once with the selected fixture IDs for that pair, not once per individual fixture.

### Resolve provider settings from current config

Doctor result files include profile and model names, but not all provider credentials/settings. The command will load current GitBench config and resolve the named profile/model to construct the same model adapter. If a model cannot be resolved from config, doctor fails with a clear message before starting reruns.

## Risks / Trade-offs

- Legacy string matching may miss some transient errors. → Keep the pattern list explicit and covered by tests; expand it only when real failures justify it.
- Current config may differ from the config used for the original run. → Print the resolved profile/model plan in dry-run and fail early when config is missing.
- Provider output is nondeterministic, so repaired scores may change from what a full rerun would have produced at the original time. → Doctor is explicitly a repair operation for invalid infrastructure failures, not a historical replay.
- Rerunning many fixtures can still hit provider limits. → Respect existing timeout/retry-count/profile settings and keep `--dry-run` available for planning.
- Local `Too many open files` failures may recur if concurrency is too high. → Default doctor execution should be conservative, with optional worker settings only if implemented carefully.
