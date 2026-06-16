## Why

GitBench currently runs each fixture once for each model, reasoning effort, and output mode, so reported pass rates can move materially because model generation, provider routing, and LLM-based judging are non-deterministic. Repeated evaluation campaigns are needed to estimate normal one-attempt reliability, distinguish stable behavior from flaky behavior, and present that evidence without flattening multiple attempts into misleading single-result UI.

## What Changes

- Add evaluation campaigns that run every selected fixture for a configurable number of complete trial rounds across each model, reasoning effort, and output mode.
- Make fixture inputs reproducible across trials by stabilizing generated Git history and recording hashes for the rendered prompt, request configuration, and benchmark inputs.
- Preserve one raw run envelope per model/effort/output-mode/trial and group those envelopes under a campaign identity with planned/completed trial counts and completion status.
- Support resumable campaigns without repeating already completed attempts, while keeping transient repair scoped to an exact campaign trial.
- Replace the ambiguous headline `pass_at_k` interpretation with explicit mean one-attempt success rate, attempt counts, stable-pass/flaky/stable-fail fixture classifications, and separately named pass-any-at-N metrics.
- Record trial-level and campaign-level cost, token, API-time, provider-route, scoring-method, and failure information so model variance is not silently mixed with infrastructure or judge variance.
- Cache deterministic LLM-judge decisions by fixture/input/output identity within a campaign and preserve judge member scores for auditability.
- **BREAKING**: advance the generated report schema and report API from one-result-per-fixture fields to campaign summaries, fixture aggregates, and separately queryable raw attempts. Historical result artifacts remain supported by importing them as one-trial legacy campaigns.
- Add campaign-aware report selection and completeness indicators throughout the web app.
- Update overview, model, benchmark, fixture, compare, history, cost, token, and runtime views to present repeated-trial aggregates with expandable raw evidence.
- Replace binary fixture comparisons such as gained/lost and agreement matrices with reliability-based comparisons when a campaign contains multiple trials.
- Update methodology and explanatory copy to describe repeated trials, uncertainty, remaining non-determinism, and the distinction between per-trial resource usage and total campaign consumption.

## Capabilities

### New Capabilities

- `evaluation-campaigns`: Campaign identity, deterministic fixture inputs, repeated trial scheduling, resume/completeness behavior, raw-attempt preservation, explicit reliability metrics, and judge/provider provenance.
- `evaluation-campaign-reporting`: Campaign selection, campaign summaries, fixture reliability aggregates, raw-attempt drilldowns, completeness states, and repeated-trial comparison semantics in generated reports and the web app.

### Modified Capabilities

- `json-export`: Export campaign metadata, explicit reliability summaries, fixture aggregates, raw-attempt references, and backward-compatible one-trial imports.
- `report-query-api`: Store and query campaigns, trials, raw fixture attempts, fixture aggregates, trial-level summaries, and campaign-scoped filters.
- `report-pages`: Make overview, model, benchmark, fixture, compare, history, and directory pages campaign-aware and replace single-result assumptions.
- `chart-components`: Render repeated-trial reliability and resource metrics without conflating trial variability with existing reasoning-effort range whiskers.
- `methodology-page`: Explain campaign methodology, mean one-attempt success, pass-any-at-N, uncertainty, deterministic inputs, judge behavior, and limitations.
- `cli-live-display`: Report campaign/trial progress, completion, and aggregate attempt counts during repeated runs.
- `runtime-tracking`: Distinguish mean per-trial API time, trial variability, and total campaign API time.
- `runtime-chart`: Present per-trial API-time comparisons separately from total campaign time.
- `pricing-pipeline`: Distinguish mean cost per complete trial from total campaign cost.
- `cost-value-chart`: Rank comparable per-trial costs while exposing total campaign spend in detail.
- `token-usage-chart`: Rank comparable per-trial token usage while exposing total campaign usage in detail.
- `model-call-reliability`: Define how exhausted transient failures affect campaign completeness and denominators rather than silently becoming quality failures.
- `llm-judge-scoring`: Cache campaign judge decisions, preserve member-level provenance, and prevent judge failures from silently changing the scoring method.

## Impact

- Python runner and CLI orchestration in `gitbench/harness/runner.py` and `gitbench/cli.py`.
- Fixture setup and Git repository generation in `gitbench/utils/git.py` and benchmark-specific setup paths.
- Result types, schema versioning, serialization, export, aggregation, repair, and report generation.
- LLM judge caching, score provenance, provider routing metadata, request configuration, and attempt telemetry.
- SQLite report schema, Python and JavaScript database builders, report-store abstraction, Vercel API routes, and TypeScript report types.
- Astro pages and React charts for campaign selection, reliability summaries, resource normalization, comparison semantics, and attempt drilldowns.
- Interaction with result-safety processing: every retained raw attempt must be reviewed/sanitized before publication, while campaign aggregates must not expose unsanitized content.
- Existing report tests, API tests, UI component tests, CLI integration tests, fixture determinism tests, and historical artifact migration coverage.
