## Why

Large benchmark runs can contain transient infrastructure failures that should not count as model-quality failures, especially provider timeouts and local resource exhaustion. The latest persisted result set already contains doctorable failures, so GitBench needs a way to repair existing result files without rerunning every model and fixture.

## What Changes

- Add a `gitbench doctor` command that accepts an existing results JSON file and reruns only doctorable failed fixture entries.
- Support `gitbench doctor --latest` to target all current result files under `gitbench-results/`.
- Add `--dry-run` so users can inspect the repair plan without invoking model providers.
- Add `--output` so users can choose a separate repaired result path for a single explicit input file.
- Update result files in place by default.
- Recompute benchmark, model, profile, and top-level summaries after replacing repaired scores.
- Keep output schema unchanged for now; doctorability is determined by hardcoded legacy error patterns.
- Do not rerun ordinary scoring failures by default.

## Capabilities

### New Capabilities
- `result-doctoring`: Detect and repair doctorable failures in existing GitBench result files by selectively rerunning affected model fixtures.

### Modified Capabilities

None.

## Impact

- CLI: adds a new `doctor` command and options.
- Harness runner: needs an internal way to run selected fixture IDs for a benchmark.
- Result handling: needs utilities to scan combined result files, replace selected scores, and recompute summaries.
- Configuration: doctor must resolve the original model profile settings from existing config so reruns use the same provider/base URL/API key behavior.
- Tests: add unit and CLI coverage for dry-run planning, in-place updates, explicit output, selective fixture reruns, summary recomputation, and non-doctorable failure preservation.
