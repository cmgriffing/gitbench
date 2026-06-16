## Context

GitBench currently treats a model, reasoning effort, output mode, and fixture as producing one authoritative result. The runner writes one result envelope per model/output-mode run, aggregation computes binary fixture outcomes, the report database stores one row per fixture result, and the web app commonly locates a result with a first-match lookup. That model cannot represent repeated attempts without losing evidence or producing ambiguous metrics.

Repeated evaluation also exposes sources of variance beyond target-model sampling:

- Fixture setup currently creates Git objects with time-dependent identities, so repeated fixture generation can change rendered prompts and expected repository state.
- Provider routing and request configuration are not fully represented in result provenance.
- LLM judging can vary independently of target-model output, and current judge failure fallback can mix scoring methods.
- Infrastructure failures, incomplete campaigns, and structured-output validation failures have different meanings and need different denominator treatment.
- Existing cost, token, and runtime charts summarize a single run and do not distinguish normal per-trial consumption from total campaign consumption.
- The Astro report is largely generated from a single static dataset, while campaign selection requires a consistent query dimension across pages and API-backed components.

At current suite and model counts, trial multiplication is material. A five-trial full campaign can require hundreds of thousands of target calls before judge and safety calls. Resume, completeness, and cost visibility are therefore core behavior rather than operational refinements.

## Goals / Non-Goals

**Goals:**

- Run every selected model, reasoning effort, output mode, and fixture for a configurable number of complete trial rounds.
- Ensure repeated trials evaluate identical fixture inputs and record enough provenance to detect invalid comparisons.
- Preserve every raw attempt while exposing explicit campaign, trial, model, benchmark, and fixture aggregates.
- Define quality, reliability, failure, cost, token, and runtime metrics without ambiguous denominator or averaging behavior.
- Resume interrupted campaigns without duplicating completed attempts.
- Make all report and web surfaces campaign-aware, including incomplete and one-trial legacy campaigns.
- Let users move from aggregate reliability to the exact raw attempts and judge evidence behind it.
- Keep historical result artifacts readable through a one-trial compatibility import.

**Non-Goals:**

- Claim that repeated trials make provider-hosted model evaluation fully deterministic.
- Add statistical significance testing or confidence-interval claims in the first version.
- Compare campaigns with different fixture sets, scoring configurations, prompts, or request configurations as if they were equivalent.
- Force a particular provider route when the provider cannot guarantee one.
- Replace the existing model, benchmark, fixture, or output-mode navigation hierarchy.
- Store unsanitized raw model content in aggregate database rows or public summary endpoints.

## Decisions

### 1. Represent repeated work as an evaluation campaign

An evaluation campaign is the top-level identity for a repeated benchmark execution. Its immutable configuration includes:

- campaign ID and creation time
- selected benchmark and fixture IDs
- selected model IDs and reasoning efforts
- selected output modes
- planned trial count
- scorer and judge configuration
- normalized target-model request configuration
- fixture-generation version and environment
- result schema version
- optional safety-review configuration

The default trial count is `3`. CLI and configuration can override it, including `1` for smoke runs. Published evaluations can choose a higher policy such as `5`; the storage and UI semantics do not depend on a particular count.

Each campaign contains complete numbered trial rounds. A trial round schedules every selected model/effort/output-mode/fixture combination once. The scheduler uses a recorded seed and balances ordering, including alternating output-mode order, to reduce temporal and provider-load bias.

### 2. Store one immutable raw envelope per execution unit

Raw artifacts are organized under:

`gitbench-results/<campaign-id>/`

The directory contains an atomically updated `campaign.json` manifest and one immutable run envelope per model, reasoning effort, output mode, and trial. Each fixture result inside that envelope is one raw attempt.

The uniqueness key is:

`(campaign_id, trial_index, model_id, reasoning_effort, output_mode, fixture_id)`

The manifest records planned, completed, valid, failed, and safety-reviewed attempt counts. Aggregate report generation consumes raw envelopes; it does not replace them.

This structure keeps current per-model run files manageable, makes partial trial recovery possible, and avoids one monolithic artifact becoming a write bottleneck.

### 3. Make fixture input identity stable and verifiable

Fixture setup must produce stable Git object identities for the same fixture-generation version and seed. Git author, committer, and reflog timestamps, identities, locale, timezone, and other relevant environment inputs are fixed explicitly.

Every attempt records:

- fixture input hash
- rendered prompt hash
- expected-output or scoring-input hash
- normalized request-configuration hash
- scorer/judge-configuration hash

Before resume or aggregation, GitBench verifies these hashes against the campaign manifest. A mismatch is an invalid attempt and makes the campaign incomplete until repaired; it is never silently averaged with compatible attempts.

### 4. Resume by exact attempt identity

Resume loads the campaign manifest and existing envelopes, verifies immutable campaign configuration and input hashes, and schedules only missing or explicitly retryable attempts. A completed valid attempt is never rerun by ordinary resume.

Transient target-provider or transport failures may be retried within the configured call policy. If retries are exhausted, the attempt remains an infrastructure failure and the campaign remains incomplete. An explicit repair command can target that exact campaign attempt without creating duplicate evidence.

Structured-output parse or schema-validation failure is a valid model-quality outcome because the model returned an unusable answer. It counts as a failed quality attempt. Missing responses, transport failures, judge exhaustion, invalid fixture hashes, and unpublished safety state do not count as model-quality failures.

### 5. Use explicit reliability metrics

For a complete balanced campaign:

- `mean_success_rate` is passing valid attempts divided by scheduled quality attempts. It is also the mean of equal-sized trial pass rates.
- `pass_any_at_n` is the share of fixtures with at least one passing attempt in the first `n` comparable attempts. It is always named separately and never labeled `pass_at_k`.
- A fixture is `stable_pass` when every valid attempt passes.
- A fixture is `flaky` when it has both passing and failing valid attempts.
- A fixture is `stable_fail` when every valid attempt fails.

Summaries expose numerator, denominator, planned trials, completed trials, valid attempts, and failure counts. Trial-level minimum, maximum, mean, and standard deviation may be shown descriptively. The first version does not present confidence intervals or significance claims.

Campaign-level rankings require complete, balanced campaigns. Incomplete campaigns remain inspectable but are excluded from default ranking and comparison unless the user explicitly includes them.

### 6. Separate target variance, judge variance, and infrastructure variance

Every attempt records target request provenance that is available from the provider, including route/provider identifiers, model identifier, normalized parameters, token usage, latency, and retry history.

LLM-judge decisions are cached within a campaign by:

`(fixture_input_hash, target_output_hash, judge_configuration_hash)`

The cache stores each judge member's score, rationale or structured result, model/provider provenance, and final aggregation. Judge failure after retries yields an unscored attempt and incomplete campaign rather than falling back to a different scoring method. This prevents target-model reliability from being mixed with scorer-method changes.

### 7. Normalize resource metrics at both trial and campaign levels

Resource summaries expose:

- mean cost per complete trial
- total campaign cost
- mean tokens per complete trial
- total campaign tokens
- mean API time per complete trial
- total campaign API time
- per-attempt distributions and failure-related consumption

Cross-model ranking charts use mean per complete trial so campaigns with different trial counts remain comparable. Total campaign consumption is shown as secondary operational context. Wall-clock duration is not treated as additive API time and is labeled separately when available.

### 8. Introduce a versioned campaign report schema

The generated report schema advances to a campaign-aware version. It contains normalized entities for:

- campaigns
- campaign trials
- raw fixture attempts
- fixture reliability aggregates
- model campaign summaries
- benchmark campaign summaries
- resource summaries
- judge-member evidence
- safety/publication state

Historical artifacts are imported as one-trial legacy campaigns. They are marked `legacy` and do not gain inferred variance. Compatibility fields may be emitted during migration, but new consumers use explicit metric names and attempt counts.

### 9. Make campaign a first-class report query dimension

The report store and HTTP API accept a campaign selector on campaign-sensitive queries. Responses include campaign identity, compatibility metadata, completeness, and legacy state.

The default selection is the latest completed publishable campaign. If no completed campaign exists, the latest incomplete campaign is shown with a prominent incomplete state. Stable page routes remain unchanged; campaign selection is represented in query state and shared by API-backed islands.

Static Astro shells continue to provide navigation and initial markup, while campaign-sensitive summaries, charts, tables, and drilldowns read through the report API/store abstraction. This avoids generating a duplicate static site for every campaign and keeps campaign changes consistent across pages.

Raw-attempt endpoints are paginated or addressed by exact attempt identity. Aggregate endpoints do not include raw prompt or output content.

### 10. Redesign report views around reliability and evidence

The web app adds a global campaign selector with trial count, completion, legacy, and comparability indicators.

- Overview shows mean one-attempt success and explicit attempt counts. Existing reasoning-effort range whiskers retain their meaning; trial variability appears in tooltips and dedicated detail, not in the same visual encoding.
- Model pages show mean success, completed trials, and stable-pass/flaky/stable-fail counts by output mode and benchmark.
- Benchmark pages render aggregate cells such as `4/5`, with accessible status labels and reliability-aware heatmaps.
- Fixture pages show per-model/output-mode attempt aggregates and expandable raw trials, including score, validation, timing, tokens, cost, provider route, and judge evidence.
- Compare replaces binary gained/lost and agreement assumptions with reliability deltas such as more reliable, less reliable, or equal, backed by fixture pass probabilities and attempt counts.
- History uses one point or row per campaign and expands to trial details. Deltas are computed only for compatible campaign configurations.
- Cost, token, and runtime views rank mean per complete trial and expose total campaign consumption separately.
- Methodology explains repeated trials, remaining non-determinism, denominator rules, judge behavior, and legacy limitations.

No status relies on color alone. Counts, labels, icons, and table text expose the same meaning for keyboard and assistive-technology users.

### 11. Gate publication on result safety when configured

Every retained raw attempt passes through the configured result-safety review before it can be exposed by public raw-attempt endpoints. Campaign publication state records reviewed, sanitized, blocked, and pending counts.

Aggregates may be computed from private raw attempts, but they cannot contain raw unsanitized content. A campaign configured to require safety review is not considered publishable until all otherwise valid attempts reach an allowed safety state.

## Risks / Trade-offs

- **Cost and duration multiply quickly.** Defaulting to three trials improves evidence but makes accidental broad runs expensive. The CLI must show the planned target, judge, and safety call budget and require existing confirmation behavior before execution.
- **Deterministic fixture generation may change fixture hashes.** The migration deliberately separates new campaigns from historical results instead of pretending they are directly comparable.
- **Provider metadata may be incomplete.** GitBench records available routing evidence and labels missing fields; it does not infer provider routes.
- **Incomplete campaigns complicate UX.** They remain visible for diagnosis, but default rankings use complete campaigns and always display denominators.
- **Static report architecture becomes more dynamic.** API-backed islands add client data loading, but avoid multiplying generated pages and centralize campaign filtering.
- **Judge caching can hide desired repeat-judge variance.** The initial product measures target-model reliability. A future explicit judge-variance study can disable or vary the cache under a distinct campaign configuration.
- **Legacy support adds schema complexity.** Marking old data as one-trial legacy campaigns provides a clear boundary and can be removed in a future major report-schema version.

## Migration Plan

1. Add deterministic fixture identity and campaign/raw-attempt result types without changing existing report readers.
2. Add repeated scheduling, manifest persistence, exact resume, and judge caching behind campaign schema output.
3. Add campaign-aware aggregation and import existing artifacts as one-trial legacy campaigns.
4. Migrate the SQLite builders, report store, API routes, and TypeScript types to campaign entities and explicit metrics.
5. Add the global campaign selector and update pages/charts incrementally, retaining legacy rendering until every surface uses campaign queries.
6. Advance the report schema version and make campaign output the default.
7. Remove ambiguous new-schema `pass_at_k` fields after compatibility consumers have migrated.

Rollback can disable repeated scheduling and generate one-trial campaigns while retaining the new schema. Raw campaign artifacts remain readable even if the web UI falls back to legacy summary rendering.

## Open Questions

- Whether published benchmark policy should require five trials while keeping the product default at three.
- Which provider-routing fields can be normalized consistently across direct providers and OpenRouter.
- Whether a later version should add bootstrap intervals or paired significance tests once campaign volume and interpretation are validated.
