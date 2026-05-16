## Why

GitBench currently reports pass rates, costs, and token usage — but not runtime. Speed is a first-class dimension for model selection: a model that costs the same and scores the same but runs 10× slower is materially worse. Users need to see which models are fastest so they can make fully informed comparisons across accuracy, cost, token usage, *and* speed.

## What Changes

- **Instrument the benchmark runner** to capture per-fixture wall-clock timing (fixture setup → model call → scoring).
- **Store runtime data** in per-fixture `Score` objects and persist it in result JSON.
- **Aggregate runtime** in `render.py` so the web UI receives per-model timing summaries (total, average, min, max).
- **Add runtime types** to the TypeScript data schema (`types.ts`).
- **Create a `RuntimeBarChart` component** — a horizontal bar chart that ranks models by total wall-clock time, mirroring the pattern of `PassRateBarChart` but ordered fastest→slowest.
- **Add the chart to the Overview page** (`/`) alongside the existing Pass Rate, Cost, and Token Usage sections.

## Capabilities

### New Capabilities
- `runtime-tracking`: Instrumentation in the benchmark runner to capture per-fixture wall-clock duration and store it in result data.
- `runtime-chart`: A React bar chart component ranking models by total runtime, with provider-colored bars, truncated labels with icons, and tooltips.

### Modified Capabilities
- `chart-components`: Add a new `RuntimeBarChart` requirement to the existing chart-components spec (delta spec for the new chart's placement and behavior).

## Impact

- **Runner**: `gitbench/harness/runner.py` — wrap each fixture execution with `time.perf_counter()`.
- **Types (Python)**: `gitbench/harness/types.py` — add `duration_ms` field to `Score` and `BenchmarkResult`.
- **Aggregation**: `gitbench/render.py` — compute per-model runtime aggregates in `aggregate_runs()`.
- **Types (TypeScript)**: `gitbench/web/src/lib/types.ts` — add `ModelRuntimeSummary` interface, extend `ModelSummary` with optional runtime fields, add `model_runtimes` to `GitBenchData`.
- **New component**: `gitbench/web/src/components/charts/RuntimeBarChart.tsx`.
- **Overview page**: `gitbench/web/src/pages/index.astro` — import and render `RuntimeBarChart`.
