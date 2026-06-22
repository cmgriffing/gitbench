## 1. Establish Dependency and Compatibility Baseline

- [x] 1.1 Confirm `fix-benchmark-scoring-regression` is implemented and its judge characterization tests pass unchanged.
- [x] 1.2 Add failing campaign-level tests showing production runners do not currently reuse identical judge decisions and cache-hit evidence loses member details.
- [x] 1.3 Define the campaign/result schema version change and actionable compatibility error for legacy judge campaigns without dedicated judge identity.

## 2. Define Judge Configuration Identity

- [x] 2.1 Build a canonical secret-free judge identity containing ordered member model/provider/reasoning/request settings, rubric version, and aggregation version.
- [x] 2.2 Compute and expose a dedicated judge configuration hash from that canonical identity.
- [x] 2.3 Add tests proving each decision-relevant change invalidates the hash while credentials and transient capacity settings do not enter persisted identity.
- [x] 2.4 Add dedicated judge identity fields to campaign configuration and raw-attempt provenance serialization.

## 3. Persist Full Campaign Cache Evidence

- [x] 3.1 Change judge cache values from aggregate floats to complete serializable `JudgeEvidence` records with explicit cache-hit state.
- [x] 3.2 Implement atomic campaign-store persistence and loading for cache evidence scoped by campaign ID.
- [x] 3.3 Implement per-evidence-key single-flight coordination so identical concurrent misses issue one ensemble call while different keys may proceed independently.
- [x] 3.4 Ensure success, partial failure, and exhausted evidence resolve all waiters and are persisted before attempt completion.

## 4. Wire Cache and Provenance Through Campaign Execution

- [x] 4.1 Create one campaign cache in campaign execution and pass it to every compatible runner and `JudgeClient` created for that campaign.
- [x] 4.2 Record the actual judge evidence configuration hash in judged attempt provenance instead of substituting the scorer configuration hash.
- [x] 4.3 Preserve original member evidence and mark reuse when a cached decision is attached to another raw attempt.
- [x] 4.4 Validate requested judge identity against the campaign manifest before resume issues target or judge calls.
- [x] 4.5 Permit non-judge campaigns without judge identity to resume while rejecting legacy judge campaigns lacking verifiable identity.

## 5. Verify Campaign Semantics

- [x] 5.1 Add end-to-end tests proving identical evidence is judged once across trials, target runners, and output modes within one campaign.
- [x] 5.2 Add restart/resume tests proving persisted evidence is reused and different campaign IDs do not share entries.
- [x] 5.3 Add cache-miss tests for changed target output, fixture input, rubric, aggregation, judge member, and judge request configuration.
- [x] 5.4 Add evidence export tests covering direct calls, cache hits, partial member failure, and complete judge exhaustion.
- [x] 5.5 Verify exhaustion remains `UNSCORED`, excluded from quality denominators, and campaign-incomplete for both direct and cached evidence paths.
- [x] 5.6 Run focused judge, runner, campaign store, resume, aggregation, export, and result-safety test suites.
