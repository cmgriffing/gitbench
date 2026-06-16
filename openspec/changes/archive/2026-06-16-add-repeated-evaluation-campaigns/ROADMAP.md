# Roadmap: Repeated Evaluation Campaigns

Change: `add-repeated-evaluation-campaigns`  
Schema: `spec-driven`  
Based on: `design.md`, `tasks.md`, and the `specs/` directory.

## Vision

GitBench moves from one-result-per-fixture reporting to repeated-trial evaluation campaigns that expose one-attempt reliability, distinguish stable from flaky behavior, and preserve every raw attempt for audit. The remaining work is delivered as vertical slices — each slice is end-to-end, demoable, and retired-risk-first.

## Success Criteria

- A user can start a campaign with a configurable number of trials, interrupt it, resume without re-running completed attempts, and inspect the resulting `campaign.json` manifest.
- Fixture inputs are deterministic across trials; any hash mismatch invalidates the affected attempts.
- LLM-judge decisions are cached by fixture-input/output/judge-config hash; judge failures leave attempts `unscored` rather than falling back to a different scorer.
- The generated report schema advances to version 2 with explicit `mean_success_rate`, `pass_any_at_n`, fixture reliability classifications, trial counts, and resource summaries.
- Historical result artifacts import as one-trial legacy campaigns without inferred stability.
- The web app has a global campaign selector; every report page and chart reads campaign-aware aggregates through the API and handles incomplete/legacy states accessibly.
- All Python and web test suites pass and `pnpm build` succeeds.

## Key Risks

1. **Cost explosion**: defaulting to three trials multiplies target, judge, and safety calls. The CLI must show the budget and require confirmation.
2. **Deterministic fixture drift**: Git author/committer timestamps, reflog entries, and environment inputs can change fixture identity across trials.
3. **Resume correctness**: silently duplicating or dropping attempts breaks reliability metrics.
4. **Schema/API churn**: campaign-aware types touch Python, SQLite, Vercel API, and Astro/React; mismatched contracts will break the build.
5. **Safety gating**: raw attempts must be reviewed before public endpoints expose them; aggregates must never include unsanitized content.

## Slices

- [ ] **S01: Deterministic fixture identity and hashing** `risk:high` `depends:[]`
  > After this: running the same fixture twice under the same campaign seed produces identical Git object SHAs and matching fixture/rendered-prompt/config hashes.

- [ ] **S02: One-trial campaign runner and manifest persistence** `risk:high` `depends:[S01]`
  > After this: `gitbench run --campaign-id ... --trials 1` writes a `campaign.json` manifest plus one immutable raw envelope per model/effort/output-mode/fixture combination.

- [ ] **S03: Exact resume, duplicate prevention, and targeted repair** `risk:high` `depends:[S02]`
  > After this: interrupting a campaign and re-running the same command schedules only the missing attempts; `gitbench repair --campaign-id ... --identity ...` retries exactly one attempt and keeps prior failure history.

- [ ] **S04: Seeded balanced scheduling and CLI progress** `risk:medium` `depends:[S02]`
  > After this: a multi-trial campaign schedules every model/effort/output-mode/fixture exactly once per numbered trial with balanced ordering; the CLI shows trial counts, target-call budget, reused attempts, failures, and publication state.

- [ ] **S05: Scoring provenance and campaign-scoped judge caching** `risk:high` `depends:[S02]`
  > After this: each raw attempt stores normalized request config, retry history, provider-route metadata, and token/latency/cost; LLM-judge results are cached by `(fixture_input_hash, target_output_hash, judge_config_hash)` and retain member-level evidence.

- [ ] **S06: Fixture reliability metrics and failure classification** `risk:high` `depends:[S02,S05]`
  > After this: a complete campaign produces fixture aggregates with `stable_pass`/`flaky`/`stable_fail` labels, explicit `mean_success_rate`, `pass_any_at_n`, numerators/denominators, and excluded operational-failure counts.

- [ ] **S07: Resource normalization, JSON export, and legacy import** `risk:medium` `depends:[S06]`
  > After this: campaign exports include mean-per-complete-trial and total campaign cost/token/API-time summaries, and historical one-result artifacts import as one-trial `legacy` campaigns without inferred variance.

- [ ] **S08: Report database schema and report-store abstraction** `risk:high` `depends:[S06]`
  > After this: the SQLite report builders contain campaign/trial/raw-attempt/aggregate/provenance/publication-state tables; the report store can list campaigns, pick a default, check compatibility, and query bounded raw attempts.

- [ ] **S09: Vercel API routes and TypeScript types** `risk:medium` `depends:[S08]`
  > After this: API endpoints serve campaign selectors, aggregate queries, and paginated/exact-identity raw-attempt queries; aggregate responses never include raw prompt/output/judge content and publication state gates raw content.

- [ ] **S10: Global campaign selector and shared query state** `risk:medium` `depends:[S09]`
  > After this: every report page renders a campaign selector showing date, trial count, completeness, publication state, legacy state, and compatibility; the selection persists across overview/model/benchmark/fixture/compare/history/directory routes.

- [ ] **S11: Reliability-aware report pages** `risk:medium` `depends:[S09,S10]`
  > After this: overview/model/benchmark/fixture/compare/history pages display mean one-attempt success, attempt counts, completed trials, reliability classifications, and expandable raw trial evidence instead of binary gained/lost comparisons.

- [ ] **S12: Campaign-aware charts and resource views** `risk:medium` `depends:[S09,S10]`
  > After this: pass-rate, heatmap, scatter, runtime, cost-value, and token charts rank mean-per-complete-trial values, disclose total campaign consumption separately, and expose accessibility labels for incomplete/legacy/non-color status.

- [ ] **S13: Methodology, safety publication, and end-to-end verification** `risk:high` `depends:[S07,S09,S11,S12]`
  > After this: methodology copy explains repeated trials and uncertainty; safety review gates every raw attempt before publication; an end-to-end fixture campaign test covers text/structured output, repeated trials, judge scoring, interruption/resume, report generation, API queries, and UI drilldown; `pytest`, `pnpm test:api`, and `pnpm build` all pass.

## Dependency Graph

```text
S01 ─┬─▶ S02 ─┬─▶ S03
     │        ├─▶ S04
     │        ├─▶ S05 ─┐
     │        │         │
     │        │         ▼
     │        │        S06 ─┬─▶ S07 ─┐
     │        │             │        │
     │        │             ▼        │
     │        │            S08 ──▶ S09 ─┬─▶ S10 ─┬─▶ S11 ─┐
     │        │                          │        │        │
     │        │                          └────────┴─▶ S12 ─┤
     │        │                                             │
     │        └─────────────────────────────────────────────┤
     │                                                      ▼
     └────────────────────────────────────────────────────▶ S13
```

## Proof Strategy

Each slice lands with a small, fast verification command:

- S01: `pytest tests/test_fixture_determinism.py -q`
- S02: run a one-trial smoke campaign against a single benchmark and inspect `campaign.json`
- S03: interrupt/resume the smoke campaign and assert no duplicate attempts
- S04: run a three-trial campaign and verify trial ordering/budget output
- S05: inspect raw-attempt provenance and judge-cache entries
- S06: aggregate synthetic raw attempts and assert reliability classifications
- S07: export the campaign and import a legacy artifact, assert round-trip
- S08: build a report DB and query campaigns/aggregates/raw attempts
- S09: call campaign API routes and verify TypeScript types compile
- S10: open a report page and assert selector state persists across routes
- S11/S12: page-level and chart tests pass with campaign switching
- S13: full integration test + `pnpm build`

## Verification Classes

| Class | Where it lives | Slices |
|---|---|---|
| Python unit tests | `tests/test_campaign*.py` | S01–S07 |
| Runner integration tests | `tests/test_runner*.py`, `tests/test_integration.py` | S02–S04, S13 |
| Scoring/judge tests | `tests/test_judge*.py` | S05–S06 |
| Aggregation/export tests | `tests/test_aggregation*.py`, `tests/test_export.py` | S06–S07 |
| Report DB/API tests | `tests/test_report_*.py` | S08–S09 |
| Web API tests | `gitbench/web/tests/**/*.test.ts` | S09 |
| Component tests | `gitbench/web/src/components/**/*.test.tsx` | S10–S12 |
| Page tests | `gitbench/web/tests/**/*.spec.ts` | S11–S13 |
| Build verification | `pnpm build` | S09–S13 |

## Definition of Done

For each slice:

- [ ] Code changes are scoped to the slice and pass the slice's verification command.
- [ ] New/changed tests are added and pass.
- [ ] `ruff check` is clean for modified Python files.
- [ ] The slice's demo line is demonstrable without manual setup.
- [ ] The `openspec/changes/add-repeated-evaluation-campaigns/tasks.md` checkboxes relevant to the slice are updated.
- [ ] No regressions in existing test suites touched by the slice.

## Requirement Coverage

| Slice | Specs covered |
|---|---|
| S01 | `evaluation-campaigns`, `model-call-reliability` |
| S02 | `evaluation-campaigns`, `cli-live-display` |
| S03 | `evaluation-campaigns` |
| S04 | `evaluation-campaigns`, `cli-live-display` |
| S05 | `llm-judge-scoring`, `model-call-reliability`, `runtime-tracking` |
| S06 | `evaluation-campaigns`, `llm-judge-scoring` |
| S07 | `json-export`, `pricing-pipeline`, `runtime-tracking` |
| S08 | `report-query-api` |
| S09 | `report-query-api` |
| S10 | `report-pages`, `evaluation-campaign-reporting` |
| S11 | `report-pages`, `evaluation-campaign-reporting` |
| S12 | `chart-components`, `cost-value-chart`, `runtime-chart`, `token-usage-chart` |
| S13 | `methodology-page`, `evaluation-campaign-reporting`, `report-pages` |

## Horizontal Checklist

Cross-cutting concerns that every slice must respect:

- [ ] Uses `CAMPAIGN_SCHEMA_VERSION` and `RESULT_SCHEMA_VERSION` consistently.
- [ ] Never exposes raw prompt/output/judge content from aggregate endpoints.
- [ ] Distinguishes `mean_success_rate` from `pass_any_at_n`; avoids `pass_at_k` ambiguity in new schema fields.
- [ ] Keeps wall-clock duration separate from summed API time.
- [ ] Marks incomplete campaigns explicitly and excludes them from default rankings.
- [ ] Preserves accessibility (counts, labels, non-color status) in UI changes.

## Boundary Map

| Slice | Produces | Consumes |
|---|---|---|
| S01 | `GitExecutor` deterministic env, `FixtureProvenance` hashes | `CampaignConfig` fixture-generation version/seed |
| S02 | `Campaign`, `RawAttempt` envelopes, `campaign.json` manifest | S01 hashes, `BenchmarkRunner`, `build_run_envelope` |
| S03 | resume/repair scheduling logic, attempt-reuse invariants | S02 manifest + raw envelopes |
| S04 | seeded scheduler, CLI budget/progress output | S02 runner |
| S05 | raw-attempt provenance fields, judge cache | S02 raw attempts, `JudgeClient` |
| S06 | `FixtureAggregate`, `ModelCampaignSummary`, `BenchmarkCampaignSummary` | S05 raw attempts + judge evidence |
| S07 | campaign JSON export, legacy import, resource summaries | S06 aggregates |
| S08 | SQLite schema, `ReportStore` campaign methods | S06 aggregates, S07 legacy data |
| S09 | Vercel routes, generated TS types | S08 report store |
| S10 | global campaign selector, query-state hooks | S09 API |
| S11 | campaign-aware pages | S09 API, S10 selector |
| S12 | campaign-aware charts | S09 API, S10 selector |
| S13 | methodology copy, safety integration, full E2E test | S07 export, S09 API, S11 pages, S12 charts |
