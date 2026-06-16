## 1. Regression Tests and Fixtures

- [x] 1.1 Add a CLI integration test proving `gitbench run --campaign-id <id> --trials 2 --output-mode text` executes twice the fixture count, persists two trials, and writes raw attempts.
- [x] 1.2 Add a restart/resume test that reloads `campaign.json` in a fresh process and schedules missing identities without relying on private `_schedule` state.
- [x] 1.3 Add a report integration test that runs or seeds a campaign directory, executes `gitbench report --no-build`, and asserts campaign JSON plus SQLite campaign tables are populated from artifacts.
- [x] 1.4 Add dimensional identity tests for same model plus multiple reasoning efforts and output modes across aggregation, SQLite insertion, and raw-attempt lookup.
- [x] 1.5 Add a campaign judge-cache test proving identical fixture-input/output/config hashes reuse the judge cache through normal scorer execution.

## 2. Persisted Campaign Planning

- [x] 2.1 Persist planned trial identities in the campaign manifest or a versioned `schedule.json` artifact when a campaign is created.
- [x] 2.2 Store scheduler version, scheduler seed, selected benchmark IDs, fixture IDs, model IDs, reasoning efforts, output modes, trial count, request config hash, scorer config hash, and fixture-generation version in the immutable config.
- [x] 2.3 Update `CampaignStore.load_manifest()` and `build_resume_plan()` to reconstruct planned identities from persisted schedule data.
- [x] 2.4 Add configuration compatibility checks that reject resume when requested CLI/config inputs differ from the persisted campaign config.

## 3. Exact Campaign Execution

- [x] 3.1 Add a campaign executor that iterates persisted schedule identities instead of calling the legacy one-shot `run_all()` loop for campaign runs.
- [x] 3.2 Extract or add runner helpers for executing a single benchmark fixture identity while reusing fixture setup, structured-output handling, model telemetry, and scoring behavior.
- [x] 3.3 Convert each completed `Score` into a `RawAttempt` with exact identity, status, model output, structured fields, provenance hashes, telemetry, provider metadata, tokens, cost, timing, retry history, and judge evidence.
- [x] 3.4 Persist each raw attempt atomically before updating campaign completion counts.
- [x] 3.5 Classify structured-output validation failures as valid quality failures and provider/transport exhaustion, hash mismatch, and judge exhaustion as excluded non-quality attempts.
- [x] 3.6 Update repair behavior to target one exact campaign identity and retain prior failure history.

## 4. Campaign Aggregation and Storage Shape

- [x] 4.1 Recompute campaign trials, state, fixture aggregates, model summaries, benchmark summaries, and resource summaries from persisted raw attempts after execution and repair.
- [x] 4.2 Update aggregate keys to preserve model, reasoning effort, output mode, benchmark, and fixture dimensions for exact summaries.
- [x] 4.3 Update campaign SQLite schema primary keys and indexes so reasoning efforts and output modes cannot collide.
- [x] 4.4 Update raw-attempt store/API identity types to include reasoning level and benchmark in exact lookups.
- [x] 4.5 Keep explicitly named rollups separate from exact summaries and avoid using rollups as headline denominators.

## 5. Report Ingestion and APIs

- [x] 5.1 Add campaign artifact discovery to `gitbench report` for directories containing `campaign.json`.
- [x] 5.2 Load campaign manifests and raw-attempt envelopes, refresh aggregates, and merge campaign report records into generated report data.
- [x] 5.3 Update JSON export to emit campaign metadata, trials, exact raw-attempt references, fixture aggregates, model/benchmark summaries, resource summaries, and unambiguous `mean_success_rate` metrics.
- [x] 5.4 Populate campaign SQLite tables from actual campaign artifacts and preserve legacy run-envelope ingestion.
- [x] 5.5 Update report-store methods and API routes to return campaign-derived rows when a campaign selector is active.
- [x] 5.6 Enforce publication/safety gating for raw prompt, output, structured payload, and judge rationale fields.

## 6. Judge Cache and Campaign Display

- [x] 6.1 Thread optional campaign scoring context through `Scorer.score()` so `llm_judge` fixtures can pass fixture-input and target-output cache keys to `JudgeClient`.
- [x] 6.2 Preserve legacy one-shot judge fallback behavior while marking campaign judge exhaustion as unscored and incomplete.
- [x] 6.3 Update campaign progress display to show planned, reused, newly completed, remaining, quality failed, infrastructure failed, invalid, unscored, and publication-state counts.
- [x] 6.4 Update non-TTY campaign progress output with the same campaign counts and failure classes.

## 7. Verification

- [x] 7.1 Run Python campaign, runner, aggregation, export, render, and CLI integration tests.
- [x] 7.2 Run `pnpm test:api` in `gitbench/web`.
- [x] 7.3 Run `pnpm build` in `gitbench/web`.
- [x] 7.4 Manually verify a mock two-trial campaign produces two trials, raw attempts, completed manifest state, campaign-aware report JSON, and populated campaign SQLite tables.
