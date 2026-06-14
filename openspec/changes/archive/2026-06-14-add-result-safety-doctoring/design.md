## Context

GitBench stores model output in several places within each fixture score. Text-mode results duplicate the assistant response in `model_output` and the assistant entry of `transcript`. Structured-mode results can additionally retain generated content in `raw_structured_output` and `parsed_payload`. Aggregation copies the public representations into report JSON and SQLite, so redacting only the rendered `model_output` would leave unsafe content in raw artifacts.

The existing `JudgeClient` is tied to commit-message scoring and numeric ensemble results. The existing `doctor` command repairs transient execution failures by rerunning fixtures. Result safety is instead a post-scoring content-classification and artifact-sanitization concern. It must not affect benchmark scores and must remain a separate client and CLI workflow.

## Goals / Non-Goals

**Goals:**

- Detect inappropriate NSFW content in every model-generated representation retained by a fixture score.
- Produce a fixed, non-model-authored public redaction marker.
- Preserve original affected artifacts outside the normal report input tree for post-analysis.
- Make sanitization auditable, idempotent, atomic, and applicable to historical and newly generated results.
- Prevent configured publication workflows from silently publishing unswept or incompletely reviewed data.
- Reuse existing model profile, credential, provider, retry, and timeout infrastructure.

**Non-Goals:**

- Changing benchmark prompts, fixture scoring, pass/fail outcomes, or retrying the benchmark model.
- Reusing or changing semantic LLM judge behavior.
- Creating a general-purpose moderation taxonomy in the first version.
- Publishing original flagged content through an authenticated report route.
- Encrypting the local backup tree or implementing retention management.

## Decisions

### Decision 1: Configure a dedicated single-model safety profile

The project config will accept:

```json
{
  "result_safety": {
    "profile": "openrouter-result-safety"
  }
}
```

The referenced entry in `models` MUST resolve to exactly one model. The implementation will reuse `resolve_profile()` and existing model adapters, but it will instantiate a dedicated safety-review client rather than `JudgeClient`.

A single model keeps decisions, audit metadata, latency, and cost predictable. Ensemble voting is valuable for subjective scoring but creates ambiguous redaction thresholds and unnecessary exposure of unsafe text to multiple providers.

Alternatives considered:

- Reuse `judge.profile`: rejected because semantic scoring and publication safety have different prompts, outputs, failure semantics, and operational ownership.
- Permit profile ensembles: deferred until there is an explicit consensus policy.
- Put a raw model ID directly under `result_safety`: rejected because it duplicates provider and credential configuration.

### Decision 2: Review one canonical generated-content bundle per score

The safety reviewer will receive a labeled, canonical bundle containing only model-generated content:

- `model_output`
- every assistant-role transcript content value
- `raw_structured_output`
- `parsed_payload`, serialized deterministically when present
- non-empty `error` and `structured_error` diagnostics retained with the score

User prompts and expected answers are excluded from classification. A score is the unit of review: if any representation is classified as inappropriate NSFW content, every generated representation in that score is redacted. This avoids leaks caused by independently classifying duplicated or canonicalized values.

The canonical bundle will be hashed with SHA-256. A command-local cache will reuse decisions for identical bundles across files and model variants.

Alternatives considered:

- Review only `model_output`: rejected because transcripts and structured-output fields can retain the original unsafe response.
- Review each field independently: rejected because it multiplies model calls and can produce inconsistent treatment of duplicated content.
- Use output length or keyword rules as the primary detector: rejected because those are useful diagnostics but not reliable content classification.

### Decision 3: Use a strict decision contract and application-owned redaction text

The reviewer response will be parsed against a narrow structured contract:

```json
{
  "decision": "allow | redact",
  "reason": "inappropriate_nsfw_content"
}
```

`reason` is required for `redact` and omitted or null for `allow`. The reviewer prompt will define NSFW content narrowly enough to avoid redacting ordinary profanity, merge-conflict syntax, or legitimate technical language. Reviewed content is delimited and treated as untrusted data, not instructions.

GitBench will replace flagged content with the exact constant:

```text
[Redacted - Reason: Inappropriate NSFW content]
```

The model never authors public replacement text. Invalid, empty, or out-of-contract responses are review failures.

Alternatives considered:

- Ask the reviewer to rewrite unsafe content: rejected because rewritten output can still be unsafe, changes benchmark meaning, and creates non-deterministic public artifacts.
- Store the reviewer explanation: rejected because it may quote the unsafe content and adds an unnecessary generated-output surface.

### Decision 4: Redaction preserves evaluation data and adds audit metadata

Redaction changes generated content fields and retained diagnostic strings that
can repeat generated content. Existing `passed`, `similarity`, token counts,
costs, durations, fixture metadata, and aggregate score fields remain
unchanged.

Each reviewed score will receive `safety_review` metadata containing:

- status (`allow` or `redacted`)
- policy version
- reviewer profile and resolved model
- review timestamp
- pre-review canonical content SHA-256
- current canonical content SHA-256
- reason code when redacted

The enclosing result artifact will receive a top-level safety marker summarizing policy version, completion status, reviewer identity, review timestamp, reviewed score count, and redacted score count. Neither metadata level contains original generated text.

The current-content hash makes repeated sweeps idempotent. A score is skipped only when its policy version matches and its current canonical content hash still matches the recorded value.

### Decision 5: Archive originals before atomic replacement

The default backup root is the fixed, repository-gitignored directory `gitbench-results-nsfw/`.

For historical files beneath `gitbench-results/`, the backup mirrors the relative source path. Only artifacts containing at least one redaction are backed up. The complete original file is copied before the sanitized source is atomically replaced. Existing backups are never overwritten; a collision receives a numeric suffix.

For newly generated runs, the unsanitized run envelope is written once to the backup root when it contains a redaction, using the same timestamp/model/mode filename convention as normal run envelopes. Normal destinations receive only the sanitized payload.

All scores in an artifact are classified before any backup or source mutation occurs. A review failure therefore leaves both the source file and backup tree unchanged.

Alternatives considered:

- Store originals beside sanitized files: rejected because report discovery recursively consumes the normal result tree.
- Store only removed snippets: rejected because complete source context is needed for later analysis and provenance.
- Overwrite an existing backup: rejected because repeated sweeps must not destroy evidence from an earlier artifact state.

### Decision 6: Provide a separate `safety-doctor` workflow

The CLI will add:

```text
gitbench safety-doctor RESULT_FILE [--dry-run]
gitbench safety-doctor --latest [--dry-run]
```

`--latest` follows the existing timestamped-directory discovery convention under `gitbench-results/`. Dry-run performs real classifications and reports file, score, and reason counts but performs no backup or write.

The traversal layer will support raw run envelopes and the combined result shapes already accepted by result/report tooling. Unsupported JSON shapes fail explicitly rather than being marked reviewed.

The command remains separate from `gitbench doctor`: one reruns failed fixtures and can change scores, while the other sanitizes stored output without model-under-test calls.

### Decision 7: Gate every serialization and configured publication path

When `result_safety` is configured, new in-memory run envelopes are reviewed before they reach:

- normal JSON result files
- `--output-dir`
- JSONL
- CSV/JSON exports
- stdout JSON
- cross-mode aggregation inputs

All serialization paths consume the same sanitized payload. If review fails, the run command exits non-zero and writes no normal output artifact.

When `result_safety` is configured, `gitbench report` validates every raw or aggregate input artifact before aggregation. Missing, incomplete, stale-policy, or hash-mismatched safety metadata causes a clear error naming the artifact and directing the user to `gitbench safety-doctor`. The report command does not implicitly call the reviewer, which keeps publication reproducible and avoids hidden network calls.

When no `result_safety` section exists, existing run and report behavior remains unchanged.

## Risks / Trade-offs

- [Risk] The safety model can produce false positives or false negatives. -> Mitigation: use a narrow policy prompt, strict response contract, explicit profile selection, policy versioning, and preserved originals for audit.
- [Risk] Sending unsafe content to a third-party reviewer increases provider exposure. -> Mitigation: configure exactly one reviewer, send only model-generated fields, and document that the selected provider receives flagged candidates.
- [Risk] Safety review adds latency and cost to every score. -> Mitigation: hash-based deduplication, idempotent metadata, and no re-review of unchanged current-policy scores.
- [Risk] A process crash during mutation could corrupt a result. -> Mitigation: finish classification first, write a complete temporary file in the same directory, fsync where practical, and atomically replace.
- [Risk] The unencrypted backup directory still contains explicit content. -> Mitigation: keep it gitignored, outside report discovery, create it only when needed, and document local access and retention responsibility.
- [Risk] Historical aggregate reports may lack enough provenance to mirror original source paths. -> Mitigation: back up the complete provided file under the same timestamp directory or a collision-safe external-file namespace.

## Migration Plan

1. Add configuration parsing and the dedicated safety-review client without enabling it in the repository config.
2. Add traversal, classification, metadata, redaction, backup, and atomic-write utilities with fixture-level tests.
3. Add `safety-doctor` and sweep existing `gitbench-results/` artifacts.
4. Add the `result_safety` profile selection to `.gitbench.json`.
5. Enable run serialization and report validation gates.
6. Add `gitbench-results-nsfw/` to `.gitignore` and document handling expectations.

Rollback consists of removing `result_safety` from config to restore legacy run/report behavior. Sanitized files can be restored manually from the backup tree when authorized; rollback MUST NOT automatically republish original flagged content.

## Open Questions

- Which concrete model profile should be selected in the repository `.gitbench.json` for the initial sweep?
- Should a later policy version include additional public-safety categories beyond inappropriate NSFW content?
