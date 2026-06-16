## Why

The repeated-evaluation campaign implementation currently plans campaigns but does not execute, persist, resume, or report them as campaigns. A verified `--campaign-id --trials 2` mock run planned 24 attempts, executed only the normal 12-fixture one-shot path, left `campaign.json` in `planned` state with zero trials/raw attempts, and emitted legacy `pass_at_k` JSON with no campaign data.

## What Changes

- Add a real campaign execution path that drives every planned trial/model/reasoning/output-mode/fixture identity through the runner and persists one raw attempt before marking it complete.
- Persist the complete schedule in the campaign manifest or a stable manifest-adjacent artifact so resume can reconstruct missing work after process restart.
- Make ordinary campaign resume reject incompatible CLI/config inputs and schedule only missing, invalidated, or explicitly repairable exact identities.
- Convert runner `Score` values into `RawAttempt` envelopes with status, provenance hashes, request telemetry, output-mode data, judge evidence, cost/tokens, and operational-failure classification.
- Recompute and save campaign trials, fixture aggregates, campaign state, and resource summaries after campaign execution and repair.
- Make report generation ingest campaign artifacts from `gitbench-results/<campaign-id>/`, emit campaign-aware JSON data, and populate the campaign SQLite tables from actual campaign data.
- Preserve exact identity dimensions in aggregation, storage, and raw-attempt lookup: campaign, trial, model, reasoning effort, output mode, benchmark, and fixture.
- Wire campaign-scoped LLM judge caching through normal `llm_judge` scoring, using fixture-input and target-output hashes rather than test-only direct cache calls.
- Keep legacy one-shot artifacts readable, but avoid presenting them as repeated campaigns or using `pass_at_k` as the campaign headline metric.

## Capabilities

### New Capabilities

- `campaign-execution-lifecycle`: Covers real repeated-trial execution, raw-attempt persistence, immutable schedule reconstruction, resume/repair behavior, exact identity dimensions, and campaign aggregate recomputation.

### Modified Capabilities

- `json-export`: Campaign report generation shall ingest campaign artifacts and export unambiguous campaign metrics and raw-attempt references instead of only legacy run aggregates.
- `report-query-api`: Campaign database and API queries shall use exact campaign identity dimensions and return selected campaign data from persisted campaign artifacts.
- `llm-judge-scoring`: Campaign scoring shall provide cache keys to judge evaluation and shall preserve unscored judge exhaustion without silently changing scoring method in campaign mode.
- `cli-live-display`: Campaign live output shall reflect actual trial execution, reused attempts, remaining attempts, failures, and completion state rather than only planned counts.

## Impact

- Python CLI orchestration in `gitbench/cli.py`, runner/scorer integration in `gitbench/harness/runner.py` and `gitbench/harness/scorer.py`, and campaign persistence in `gitbench/harness/campaign_store.py`.
- Campaign model and aggregation code in `gitbench/harness/campaign.py`, `gitbench/harness/aggregation.py`, and `gitbench/harness/scheduler.py`.
- Report ingestion/export in `gitbench/render.py`, `gitbench/export.py`, SQLite schema/data builders, and web report-store/API routes.
- Tests for CLI campaign execution, interruption/resume, report ingestion, dimensional identity, judge cache use, and legacy compatibility.
