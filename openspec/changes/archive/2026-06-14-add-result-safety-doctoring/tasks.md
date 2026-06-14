## 1. Configuration and Reviewer Client

- [x] 1.1 Add `load_result_safety_config()` in `gitbench/config.py` to validate `result_safety.profile`, resolve the referenced profile, and require exactly one model
- [x] 1.2 Add configuration tests for absent, valid, missing, empty, and multi-model result-safety profiles
- [x] 1.3 Create a dedicated result-safety reviewer client with a versioned NSFW policy prompt and strict `allow`/`redact` response parsing
- [x] 1.4 Add reviewer-client tests for valid decisions, malformed responses, unsupported reason codes, adapter failures, and untrusted-content prompt isolation

## 2. Result Traversal and Classification

- [x] 2.1 Add a result-safety module that traverses raw run envelopes and supported combined result payloads without depending on benchmark scoring classes
- [x] 2.2 Build a deterministic per-score content bundle from `model_output`, assistant transcript entries, `raw_structured_output`, `parsed_payload`, and retained diagnostic strings, excluding explicit user-authored fields
- [x] 2.3 Add SHA-256 hashing and command-local decision caching so identical generated-content bundles are reviewed once
- [x] 2.4 Add traversal and bundle tests covering text mode, structured mode, absent optional fields, duplicate bundles, and unsupported payload shapes

## 3. Redaction and Audit Metadata

- [x] 3.1 Implement the fixed `[Redacted - Reason: Inappropriate NSFW content]` replacement for `model_output` and every assistant transcript content value
- [x] 3.2 Implement structured-output redaction for `raw_structured_output` and `parsed_payload` without retaining original generated strings
- [x] 3.3 Add score-level safety metadata with decision, reason, policy version, reviewer identity, timestamps, and pre/current content hashes
- [x] 3.4 Add artifact-level completion metadata with reviewed and redacted score counts
- [x] 3.5 Implement idempotent skipping for unchanged current-policy scores and re-review for stale policy or hash mismatches
- [x] 3.6 Add regression tests proving redaction sanitizes retained diagnostics while preserving scoring, token, cost, timing, fixture metadata, and benchmark summaries

## 4. Backup and Atomic File Handling

- [x] 4.1 Add `gitbench-results-nsfw/` to the repository `.gitignore`
- [x] 4.2 Implement mirrored historical-file backups beneath `gitbench-results-nsfw/` only when an artifact contains redactions
- [x] 4.3 Implement collision-safe backup naming that never overwrites an existing original
- [x] 4.4 Implement temporary-file serialization and atomic source replacement after all classifications and required backups succeed
- [x] 4.5 Add tests proving a classification or backup failure leaves the source unchanged and creates no partial sanitized artifact
- [x] 4.6 Add tests for mirrored paths, collisions, clean artifacts without backups, and complete unsanitized backup contents

## 5. Historical Safety-Doctor CLI

- [x] 5.1 Add `gitbench safety-doctor RESULT_FILE` with progress and reviewed/redacted summary output
- [x] 5.2 Add `--latest` discovery using timestamped directories beneath `gitbench-results/`
- [x] 5.3 Add `--dry-run` that performs classification but writes no backups or result changes
- [x] 5.4 Add CLI tests for explicit files, latest discovery, dry-run, unsupported formats, missing configuration, and fail-closed reviewer errors

## 6. New Run Serialization Gate

- [x] 6.1 Refactor run output handling so each completed raw run envelope passes through one result-safety gate before any normal serialization
- [x] 6.2 Route output-directory JSON, default JSON, JSONL, CSV/JSON export, stdout JSON, and cross-mode aggregation through the sanitized payload
- [x] 6.3 Write one unsanitized backup run envelope beneath `gitbench-results-nsfw/` when an in-memory run payload contains redactions
- [x] 6.4 Ensure safety-review failure exits non-zero before writing any normal artifact for the affected payload
- [x] 6.5 Add integration tests proving every output destination receives the same sanitized content and evaluation values remain unchanged
- [x] 6.6 Add integration tests proving failed safety review produces no normal JSON, JSONL, export, stdout JSON, or aggregate output

## 7. Report Publication Gate

- [x] 7.1 Add validation helpers for artifact-level completion, current policy version, score metadata, and current-content hashes
- [x] 7.2 Validate every raw and aggregate report input before aggregation when `result_safety` is configured
- [x] 7.3 Make report validation errors name the rejected artifact and direct the user to `gitbench safety-doctor`
- [x] 7.4 Ensure report validation performs no reviewer model calls and writes no updated report JSON or SQLite database on failure
- [x] 7.5 Add report tests for reviewed inputs, missing metadata, stale policy, modified content, aggregate inputs, and unconfigured legacy behavior

## 8. Documentation and End-to-End Verification

- [x] 8.1 Document the `result_safety.profile` configuration, single-model requirement, provider exposure, fixed backup location, and fail-closed behavior in `README.md`
- [x] 8.2 Document `safety-doctor`, dry-run, historical sweeping, report gating, and local retention responsibility for `gitbench-results-nsfw/`
- [x] 8.3 Add a repository single-model safety profile example without hardcoding credentials; enable `result_safety` only after a reviewer model is selected
- [x] 8.4 Run focused config, result-safety, CLI, render, and export tests
- [ ] 8.5 Run the full Python test suite and verify existing transient-failure doctor and semantic judge behavior remain unchanged
- [ ] 8.6 Perform a dry-run sweep of current timestamped results, review only counts and identifiers in terminal output, then apply the sweep after confirming the selected reviewer profile
- [ ] 8.7 Generate the report from sanitized results and verify no report JSON, SQLite, or static-site artifact contains original redacted content
