## Context

`add-repeated-evaluation-campaigns` introduced campaign model types, scheduler helpers, aggregation helpers, SQLite tables, and web API scaffolding, but the production path still behaves like the legacy one-shot runner.

Current verified behavior:

- `gitbench run --campaign-id cmp-review-trials2 --trials 2 --benchmark reflog --model mock --output-mode text` prints a plan for 24 attempts.
- The actual run executes 12 fixtures once, writes a legacy result JSON with `pass_at_k`, and emits no campaign data.
- `gitbench-results/<campaign-id>/campaign.json` remains `state: planned` with no persisted trials and no raw attempts.
- Reloading that manifest produces a resume plan with zero needed attempts because the schedule only lived in a private `_schedule` attribute.
- `gitbench report` never ingests `campaign.json` or campaign envelopes, so the campaign-aware report tables are only reachable from manually shaped data.

The corrective implementation needs to connect the existing campaign model to the real CLI and report pipeline without losing legacy artifact compatibility.

## Goals / Non-Goals

**Goals:**

- Make `--campaign-id --trials N` execute exactly the planned campaign identities.
- Persist enough schedule and configuration data for restart-safe resume.
- Store one raw attempt per exact campaign identity before counting it complete.
- Preserve exact dimensions in aggregates and APIs: campaign, trial, model, reasoning effort, output mode, benchmark, and fixture.
- Ingest campaign artifacts into `gitbench report` and expose campaign metrics through JSON, SQLite, and API routes.
- Wire campaign-scoped judge caching through normal `llm_judge` scoring.
- Add end-to-end tests that fail on the verified one-shot behavior.

**Non-Goals:**

- Rebuilding the whole web UI design.
- Adding statistical significance or confidence intervals.
- Removing legacy run-envelope ingestion.
- Changing non-campaign one-shot benchmark behavior except where shared types need compatibility.

## Decisions

### 1. Add a campaign executor above `BenchmarkRunner`

The current `BenchmarkRunner.run_all()` works at model/benchmark/output-mode granularity and returns legacy `BenchmarkResult` dictionaries. Campaign execution needs a different outer loop:

```
campaign schedule
  trial 1
    identity(model, effort, mode, fixture)
      setup fixture
      call model
      score
      write RawAttempt
      refresh counts
  trial 2
    ...
```

Decision: add a campaign execution layer that can run one exact identity at a time while reusing fixture setup, model generation, structured-output handling, and scoring code from the runner.

Alternative considered: loop `BenchmarkRunner.run_all()` N times and infer trial identity from result order. Rejected because it cannot resume exact missing attempts safely and cannot persist attempts before the whole run returns.

### 2. Persist schedule data, not private runtime state

The scheduler output must be serialized in the manifest or as a stable `schedule.json` under the campaign directory. The manifest should record the scheduler version and seed, and each trial should contain its planned identities.

Decision: persist trial identity lists as part of campaign planning and load them on resume. The resume plan must not rely on a private `_schedule` attribute.

Alternative considered: recompute the schedule every time from config. Rejected as the only source of truth because future scheduler changes could alter order; recomputation is acceptable only when the persisted scheduler version matches.

### 3. Convert `Score` into `RawAttempt` at the execution boundary

Campaign attempts should retain model output, structured-output fields, request telemetry, route metadata, token/cost usage, timing, judge evidence, and provenance hashes. `Score.operational_failure` and `Score.unscored` should map to non-quality attempt statuses.

Decision: make the campaign executor responsible for converting runner outputs into `RawAttempt` envelopes and writing each envelope atomically.

Alternative considered: make `BenchmarkRunner` return `RawAttempt` directly. Rejected for now because the runner still serves legacy output paths.

### 4. Aggregate by comparable dimensions

Fixture, model, and raw-attempt lookups currently collapse dimensions in places. Campaign aggregates must distinguish model, reasoning effort, output mode, benchmark, and fixture where the UI or API presents variant-specific reliability.

Decision: update campaign aggregate keys and SQLite primary keys/indexes to preserve exact dimensions. Cross-model or cross-mode rollups may exist, but they must be named as rollups and must not replace exact summaries.

Alternative considered: keep coarse fixture/model aggregates and let drilldowns split attempts dynamically. Rejected because headline denominators would be wrong for campaigns with multiple output modes or reasoning efforts.

### 5. Report ingestion reads campaign artifacts directly

`gitbench report` should detect campaign directories containing `campaign.json` and attempt envelopes, build campaign report records, and merge them with legacy aggregate data.

Decision: add campaign artifact loading to `render.py`/report command before SQLite generation. Legacy run envelopes remain supported and may be imported as one-trial legacy campaigns only when explicitly used for campaign compatibility.

Alternative considered: require users to manually export a campaign report first. Rejected because the normal report command is the public reporting workflow.

### 6. Judge cache keys flow through scorer context

The `JudgeClient` cache is currently test-accessible but normal scoring never supplies a cache key. Campaign scoring has the data needed to compute `(fixture_input_hash, target_output_hash)`.

Decision: thread optional scoring context through `Scorer.score()` for campaign runs so `llm_judge` fixtures pass cache keys to `JudgeClient`.

Alternative considered: have `JudgeClient` derive hashes from raw prompt/output internally. Rejected because fixture input identity belongs to campaign provenance, not the judge client.

## Risks / Trade-offs

- Existing runner code was built around benchmark batches, so exact-attempt execution may duplicate some setup/scoring glue. Mitigation: extract shared helper functions only where the duplication becomes concrete.
- Persisting full schedules grows manifest size. Mitigation: fixture/model counts are modest compared with raw outputs, and exact resume correctness matters more.
- Updating SQLite primary keys may require test fixture changes. Mitigation: keep legacy tables intact and add/adjust campaign tables only.
- Campaign report ingestion can accidentally double-count if both campaign artifacts and legacy exported run files are present. Mitigation: campaign directories should be identified by `campaign.json`, and their internal raw attempts should be the campaign source of truth.

## Migration Plan

1. Add failing CLI/report integration tests that reproduce the verified `--trials 2` one-shot behavior.
2. Persist planned trial identities during campaign creation.
3. Implement exact-identity campaign execution and raw-attempt writes.
4. Recompute/save campaign counts and aggregates after every run and after repair.
5. Add report ingestion for campaign directories and populate campaign-aware JSON/SQLite records.
6. Update report-store/API identity keys and tests for reasoning/output-mode separation.
7. Wire judge cache keys through campaign scoring and add a test proving repeated identical outputs call the judge once.
8. Keep legacy run ingestion and one-shot reports working throughout.

Rollback: disable the campaign executor behind `--campaign-id` handling and fall back to one-trial legacy output while leaving campaign artifacts readable for diagnosis.

## Open Questions

- Should campaign raw attempts be written one file per attempt, or one envelope per model/effort/output-mode/trial containing fixture attempts as originally proposed?
- Should non-campaign `llm_judge` exhaustion keep the current SequenceMatcher fallback indefinitely, or should a later change remove fallback globally?
- Should the default `gitbench report` include incomplete campaigns automatically, or require an explicit flag when no complete campaign exists?
