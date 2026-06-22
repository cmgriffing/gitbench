## Context

The LLM-judge specifications require campaign-scoped reuse keyed by fixture input, target output, and judge configuration, plus auditable member evidence. The scorer computes and passes cache keys, but production runners construct `JudgeClient` without a cache. The current cache stores only an aggregate float, cache-hit evidence omits members, and attempt provenance assigns the scorer configuration hash to the judge configuration field. Resume validation also lacks a dedicated decision-complete judge identity.

This change follows `fix-benchmark-scoring-regression`; it assumes fixture-driven judge routing is protected by runner-level characterization tests.

## Goals / Non-Goals

**Goals:**

- Reuse identical judge decisions across all compatible attempts in one campaign, including resume after restart.
- Prevent duplicate concurrent judge calls for the same evidence identity.
- Make judge configuration identity cover every input that can change a decision.
- Persist accurate judge provenance and validate it on resume.
- Preserve full auditable evidence on cache hits.

**Non-Goals:**

- Change which fixtures use `llm_judge`.
- Change judge thresholds or ensemble averaging.
- Share cache entries across campaigns.
- Persist API secrets or raw credentials.
- Repair benchmark-specific scoring dispatch.

## Decisions

### Own one durable cache per campaign

Campaign execution will create one `JudgeCache` through `CampaignStore` and pass it to every runner created for that campaign. Cache entries will be persisted atomically under the campaign directory and loaded on resume. Legacy one-shot runs may use an in-memory cache, but without campaign cache keys their behavior remains unchanged.

A runner-local cache was rejected because identical evidence produced by different target runners or output modes would not be reused. A process-only campaign cache was rejected because restart would discard paid judge decisions.

### Cache full judge evidence

Cache values will contain the complete `JudgeEvidence`, not only the final score. A cache hit will return a copy marked as cached while preserving the original member scores, member failures, aggregation method, provider-route metadata, and judge configuration hash.

This makes cached and uncached attempts equally auditable. Persisting only the aggregate was rejected because it cannot satisfy member-evidence requirements.

### Use per-key single-flight concurrency

The cache will coordinate concurrent requests by evidence key. The first caller evaluates the judge ensemble; callers for the same key wait and reuse its result. Different keys may evaluate concurrently. Cache mutation and persistence will be synchronized.

Holding one global lock during all network calls was rejected because it would serialize unrelated judge evaluations.

### Define a decision-complete judge configuration hash

The judge hash will be computed from a canonical, secret-free structure containing the ordered judge members and their model/provider/reasoning/request settings, the judge prompt or rubric version, and the aggregation algorithm/version. Any of those changes produces a cache miss and resume incompatibility.

Target-model request configuration is not part of judge identity; its effects are represented by the target output hash. Secrets and transient capacity settings are excluded because they do not define the judging decision.

### Persist and validate dedicated judge provenance

Campaign configuration and raw attempt provenance will carry the actual judge configuration hash separately from scorer configuration. Resume compatibility will compare the requested judge identity with the manifest before issuing target or judge calls.

Judge campaigns created before the dedicated hash exists will not be silently resumed. The CLI will require a new campaign or an explicit migration tool if one is later provided.

## Risks / Trade-offs

- [Risk] Durable evidence may contain publication-sensitive rationale or provider metadata. -> Mitigation: reuse existing result safety rules and avoid persisting credentials.
- [Risk] A crash after judge completion but before atomic cache persistence can cause one repeated call. -> Mitigation: write cache evidence atomically before completing the scored attempt.
- [Risk] Single-flight waiters could hang if the owner fails unexpectedly. -> Mitigation: always resolve waiters with success or failure evidence in a `finally` path and apply a bounded wait.
- [Risk] Hash inputs can drift from actual judge behavior. -> Mitigation: centralize the canonical identity next to judge construction and test each decision-relevant field.
- [Risk] Legacy campaign resume becomes stricter. -> Mitigation: fail with an actionable incompatibility message rather than reusing unverifiable judge evidence.

## Migration Plan

1. Land and verify `fix-benchmark-scoring-regression`.
2. Add the dedicated judge configuration identity and manifest fields with schema-version handling.
3. Add full-evidence cache serialization and per-key single-flight behavior.
4. Wire one cache through campaign execution and runner construction.
5. Add resume compatibility checks and end-to-end campaign tests.
6. Require new campaign IDs for legacy judge manifests without dedicated judge identity.

Rollback disables durable cache wiring while retaining new fields. Campaigns created with the newer schema must not be resumed by code that cannot validate their judge identity.

## Open Questions

- Whether cached judge evidence should retain raw judge response text if raw responses are added later; current evidence stores parsed results and errors only.
