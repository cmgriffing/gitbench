## Why

Campaign judge scoring defines cache reuse, configuration-sensitive invalidation, and auditable member evidence, but production wiring does not currently provide a campaign-scoped cache and records incomplete judge provenance. These gaps can cause duplicate judge calls, misleading provenance, and evidence loss on cache hits or campaign resume.

## What Changes

- Provide one campaign-scoped judge cache shared by compatible runners participating in the campaign.
- Make cache reuse safe under concurrent scoring and define its behavior across process restart and campaign resume.
- Include all decision-relevant judge inputs in judge configuration identity, including judge models, prompt/rubric version, aggregation rule, and request configuration.
- Persist the actual judge configuration hash in attempt provenance and validate it during resume.
- Preserve auditable member-level evidence and explicit cache-hit provenance when a cached decision is reused.
- Add campaign-level end-to-end tests covering cache hits, cache misses, evidence, exhaustion, and resume compatibility.
- Depend on `fix-benchmark-scoring-regression` so judge hardening is evaluated against the corrected scoring boundary.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `llm-judge-scoring`: Complete production cache wiring, judge configuration identity, cache-hit evidence, and concurrency behavior.
- `campaign-execution-lifecycle`: Persist and validate accurate judge provenance for raw attempts and resumed campaigns.
- `evaluation-campaigns`: Make judge configuration part of immutable campaign identity and define cache behavior across restart and resume.

## Impact

- Affects `JudgeCache`, `JudgeClient`, `BenchmarkRunner` construction, campaign runner factories, campaign configuration/provenance models, attempt persistence, resume validation, exported judge evidence, and campaign tests.
- May require a campaign/result schema migration if durable cache evidence or a dedicated judge configuration hash is added to persisted manifests.
- Changes judge call counts and cost through cache reuse, but does not change fixture routing, judge scoring thresholds, or ensemble averaging semantics.
