## Why

Benchmark models can emit explicit sexual or otherwise unsafe content that is then preserved in raw result files and published through generated reports. GitBench needs a configurable, auditable safety pass that removes inappropriate output before publication while retaining an isolated original copy for authorized post-analysis.

## What Changes

- Add a post-scoring result-safety doctor that uses a separately configured LLM profile to classify model-generated output as allowed or requiring redaction.
- Add a `result_safety` section to `.gitbench.json` for selecting the safety-review model profile.
- Require the safety reviewer to return a strict structured decision and reason; GitBench, not the reviewer, generates the public redaction text.
- Redact every stored representation of flagged model output, including `model_output`, assistant transcript content, raw structured output, and parsed structured payloads.
- Preserve benchmark scoring, pass/fail, token, cost, and timing data when content is redacted.
- Attach audit metadata describing the safety decision without retaining the original content in the sanitized artifact.
- Copy each affected original result file into a mirrored, gitignored `gitbench-results-nsfw/` tree before replacing the source file.
- Add a CLI workflow for dry-running and applying the safety pass to historical result files.
- Run the safety pass before newly generated results are serialized to normal result, JSONL, export, or stdout destinations.
- Fail closed when configured safety review cannot complete, and prevent report generation from publishing result artifacts that have not successfully completed the configured safety pass.

## Capabilities

### New Capabilities

- `result-safety-doctoring`: Configurable LLM classification, comprehensive output redaction, original-artifact backup, audit metadata, historical CLI sweeping, run-output integration, and publication gating.

### Modified Capabilities

None.

## Impact

- Configuration loading and validation in `gitbench/config.py` and `.gitbench.json`.
- New safety-review and redaction logic, likely adjacent to but separate from transient-failure result doctoring.
- CLI run, doctor-style maintenance, export, stdout, JSONL, and report-generation paths in `gitbench/cli.py`.
- Raw result score representations defined in `gitbench/harness/types.py`, including transcript and structured-output fields.
- Result aggregation and report ingestion in `gitbench/render.py`.
- Repository ignore rules and documentation for `gitbench-results-nsfw/`.
- Tests for configuration, classification responses, comprehensive redaction, backups, idempotency, output-path integration, and fail-closed publication behavior.
