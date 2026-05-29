## Why

GitBench currently treats model concurrency and fixture concurrency as independent knobs, so a run can unintentionally multiply API calls against the same upstream rate-limit bucket. This is especially painful with OpenRouter profiles that contain many upstream model IDs and several GitBench effort variants per model.

## What Changes

- Introduce capacity-aware scheduling based on request budgets rather than raw model-worker counts.
- Derive concurrency capacity groups from configured model strings after stripping GitBench effort suffixes.
- Infer OpenRouter upstream provider/model-family groups from model IDs, so related models such as `anthropic/claude-opus-4.7:max` and `anthropic/claude-opus-4.8:max` share an Anthropic Opus capacity bucket.
- Add explicit config overrides for transports or model families where safe inference is unavailable or incorrect.
- Treat GitBench effort as a provider-agnostic execution dimension and include `max` as a valid effort value.
- Preserve deterministic result ordering and existing output shapes while changing how concurrent work is scheduled.

## Capabilities

### New Capabilities
- `capacity-aware-concurrency`: Defines request-budget scheduling, inferred capacity groups, and explicit concurrency override behavior.

### Modified Capabilities
- `reasoning-level-config`: Adds `max` to the valid effort set, clarifies provider-agnostic effort parsing, and requires effort stripping before model identity/grouping.
- `reasoning-level-forwarding`: Clarifies that adapters receive base model ID plus GitBench effort, and transports may forward, translate, or ignore effort according to provider support.

## Impact

- Affected code: `gitbench/cli.py`, `gitbench/harness/runner.py`, `gitbench/harness/model.py`, `gitbench/harness/reasoning.py`, and config loading/validation in `gitbench/config.py`.
- Affected CLI behavior: `--model-workers` and `--fixture-workers` remain accepted but scheduling must respect global and per-capacity request budgets.
- Affected config: model profiles may add optional concurrency settings and explicit group overrides.
- Affected tests: CLI scheduling tests, reasoning/effort parsing tests, model adapter tests, and parallel fixture tests need coverage for budget enforcement and deterministic output.
