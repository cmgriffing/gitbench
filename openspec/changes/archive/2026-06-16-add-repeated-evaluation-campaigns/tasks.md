## 1. Campaign Contracts and Schema

- [x] 1.1 Add campaign, trial, raw-attempt, fixture-aggregate, completeness, provenance, and resource-summary types to the Python result model.
- [x] 1.2 Define the versioned `campaign.json` manifest and immutable campaign configuration hash.
- [x] 1.3 Define exact attempt identity and status enums that distinguish quality failure, operational failure, invalid input, unscored, and safety state.
- [x] 1.4 Advance the generated report schema with explicit `mean_success_rate`, `pass_any_at_n`, numerator, denominator, and trial-count fields.
- [x] 1.5 Add serialization round-trip tests for complete, incomplete, one-trial, and safety-gated campaign artifacts.

## 2. Deterministic Fixture Inputs

- [x] 2.1 Stabilize Git author, committer, reflog timestamps, identities, timezone, locale, and other relevant repository-generation inputs.
- [x] 2.2 Add fixture input, rendered prompt, expected/scoring input, request configuration, and scorer configuration hashing.
- [x] 2.3 Persist fixture-generation version, scheduler seed, and expected hashes in the campaign manifest.
- [x] 2.4 Reject or invalidate attempts whose fixture or configuration hashes differ from the campaign manifest.
- [x] 2.5 Add determinism tests that generate every fixture repeatedly and assert identical Git state and hashes.

## 3. Campaign Runner and Resume

- [x] 3.1 Add CLI and configuration support for campaign ID and configurable trial count with a default of three.
- [x] 3.2 Build complete numbered trial schedules for every selected model, effort, output mode, and fixture combination.
- [x] 3.3 Add seeded, balanced attempt ordering that alternates output-mode and model ordering across trial rounds.
- [x] 3.4 Persist immutable per-model/effort/output-mode/trial envelopes and atomically update campaign completion counts.
- [x] 3.5 Implement exact resume that reuses compatible valid attempts and schedules only missing, invalidated, or explicitly repairable identities.
- [x] 3.6 Scope transient repair to an exact campaign attempt while retaining prior retry and failure history.
- [x] 3.7 Update CLI planning and live progress output with trial counts, target-call totals, judge/safety call estimates, reused attempts, failures, and publication state.
- [x] 3.8 Add runner integration tests for complete campaigns, interruption/resume, duplicate prevention, configuration mismatch, and targeted repair.

## 4. Scoring, Reliability, and Provenance

- [x] 4.1 Classify structured-output parse and schema failures as model-quality failures while excluding exhausted transport/provider failures from quality denominators.
- [x] 4.2 Record normalized target request configuration, retry history, token usage, latency, and available provider-route metadata for every attempt.
- [x] 4.3 Add campaign-scoped LLM-judge caching keyed by fixture input, target output, and judge configuration hashes.
- [x] 4.4 Persist member-level judge results, aggregation, provenance, and failure states.
- [x] 4.5 Remove heuristic scoring fallback after exhausted judge failures and mark affected attempts unscored and campaigns incomplete.
- [x] 4.6 Compute fixture `stable_pass`, `flaky`, and `stable_fail` classifications and explicit `mean_success_rate` and `pass_any_at_n` metrics.
- [x] 4.7 Add scoring tests for mixed outcomes, invalid structured output, operational exclusion, judge cache reuse, judge config changes, and judge exhaustion.

## 5. Aggregation, Resources, and Export

- [x] 5.1 Add trial, fixture, model, benchmark, and campaign aggregation from immutable raw attempts.
- [x] 5.2 Require complete balanced summaries for default rankings while retaining inspectable incomplete aggregates and exclusion counts.
- [x] 5.3 Aggregate mean and total cost, tokens, and API time at attempt, complete-trial, and campaign scopes.
- [x] 5.4 Keep wall-clock duration separate from summed API time and retain resource consumption from failed calls.
- [x] 5.5 Reconcile target, retry, judge, and configured safety costs and mark totals partial when pricing is unavailable.
- [x] 5.6 Export campaign metadata, trial summaries, fixture aggregates, resource summaries, judge evidence, and raw-attempt references in the new JSON schema.
- [x] 5.7 Import historical result artifacts as one-trial legacy campaigns without inferring stability metrics.
- [x] 5.8 Add aggregation and migration golden tests covering complete, incomplete, incompatible, legacy, and partial-pricing data.

## 6. Report Database and Query API

- [x] 6.1 Extend both report database builders with campaign, trial, raw-attempt, aggregate, provenance, and publication-state tables and indexes.
- [x] 6.2 Add migration/import handling that maps historical rows to one-trial legacy campaigns.
- [x] 6.3 Extend the report-store abstraction with campaign listing, default selection, compatibility checks, aggregate queries, and bounded raw-attempt queries.
- [x] 6.4 Add campaign selectors and resolved campaign metadata to campaign-sensitive Vercel API routes.
- [x] 6.5 Add exact-identity or paginated raw-attempt endpoints that do not embed raw outputs in aggregate responses.
- [x] 6.6 Enforce safety/publication state before public endpoints return raw prompt, output, or judge content.
- [x] 6.7 Update TypeScript report types and generated fixtures for the campaign-aware API.
- [x] 6.8 Add Python and web API tests for campaign filtering, default selection, completeness, pagination, compatibility, legacy import, and safety gating.

## 7. Campaign Selection and Shared Web State

- [x] 7.1 Add a global campaign selector showing date, trial count, completeness, publication state, legacy state, and compatibility metadata.
- [x] 7.2 Preserve campaign selection in report query state and internal navigation across overview, model, benchmark, fixture, compare, history, and directory routes.
- [x] 7.3 Convert campaign-sensitive static data reads to API-backed islands using the report-store campaign selector.
- [x] 7.4 Add loading, empty, unavailable, incomplete, and legacy states for campaign-sensitive components.
- [x] 7.5 Add component tests for default campaign resolution, selection persistence, keyboard operation, and incomplete/legacy labels.

## 8. Reliability-Aware Report Pages

- [x] 8.1 Update overview summaries and leaderboards to show mean one-attempt success, explicit attempt counts, completed trials, and completeness.
- [x] 8.2 Update model detail pages with stable-pass, flaky, and stable-fail counts by benchmark and output mode.
- [x] 8.3 Update benchmark tables and heatmaps to show reliability ratios such as `4/5` with accessible classification labels.
- [x] 8.4 Update fixture detail pages with model/output-mode aggregates and expandable raw trial evidence.
- [x] 8.5 Replace binary gained/lost and agreement comparisons with fixture reliability deltas and paired pass-probability displays.
- [x] 8.6 Update history to use one primary row or point per campaign, nested trial detail, and compatibility-gated deltas.
- [x] 8.7 Add page-level tests for campaign switching, incomplete campaigns, raw drilldowns, output-mode comparison, and incompatible history.

## 9. Campaign-Aware Charts and Resource Views

- [x] 9.1 Update chart data contracts and tooltips with campaign ID, passing and valid attempts, planned and completed trials, and completeness.
- [x] 9.2 Preserve reasoning-effort whisker semantics and present repeated-trial variability through a distinct labeled encoding or detail view.
- [x] 9.3 Update pass-rate, heatmap, scatter, and time-series charts to use campaign reliability aggregates.
- [x] 9.4 Update runtime charts to rank mean API time per complete trial and show total campaign API time separately.
- [x] 9.5 Update cost-value charts to plot mean complete-trial cost against mean one-attempt success and disclose total campaign cost.
- [x] 9.6 Update token charts to rank mean tokens per complete trial and disclose total campaign and reasoning-token usage.
- [x] 9.7 Add chart tests for denominator display, incomplete exclusion, partial pricing, distinct variability encodings, and accessible non-color status.

## 10. Methodology, Safety, and End-to-End Verification

- [x] 10.1 Rewrite methodology content to explain campaigns, non-determinism, deterministic inputs, mean success, `pass_any_at_n`, classifications, exclusions, judge caching, resource normalization, and legacy limits.
- [x] 10.2 Remove or revise deterministic/reproducible claims that overstate guarantees from the report UI and supporting copy.
- [x] 10.3 Integrate campaign publication with result-safety review so every retained raw attempt is reviewed or sanitized before public exposure.
- [x] 10.4 Add an end-to-end fixture campaign covering text and structured output, repeated trials, judge scoring, interruption/resume, report generation, API queries, and UI drilldown.
- [x] 10.5 Verify Python unit and integration suites, report generation tests, `pnpm test:api`, web component tests, and `pnpm build`.
- [x] 10.6 Generate a compatibility report from historical artifacts and confirm one-trial legacy campaigns render without implied stability.
- [x] 10.7 Document rollout defaults, estimated call multiplication, storage growth, repair procedure, and rollback to one-trial campaigns.
