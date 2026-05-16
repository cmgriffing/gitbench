## 1. Python types — add duration_ms to Score

- [x] 1.1 Add `duration_ms: float | None = None` field to the `Score` dataclass in `gitbench/harness/types.py`
- [x] 1.2 Update `Score.to_dict()` to include `duration_ms` when not None
- [x] 1.3 Update `Score.from_dict()` to accept and set `duration_ms`
- [x] 1.4 Add `total_duration_ms` computed field to `BenchmarkResult.to_dict()` (sum of non-null score durations)

## 2. Runner — instrument fixture execution with timing

- [x] 2.1 Wrap `_run_fixture()` in `gitbench/harness/runner.py` with `time.perf_counter()` before and after
- [x] 2.2 Set `score.duration_ms` from the elapsed time (converted to milliseconds) before returning

## 3. Aggregation — compute model_runtimes in render.py

- [x] 3.1 In `aggregate_runs()`, track per-model duration sums, averages, mins, maxes from score `duration_ms` values
- [x] 3.2 Output `model_runtimes` dict with `total_ms`, `avg_ms`, `min_ms`, `max_ms`, `fixture_count` per model
- [x] 3.3 Include `model_runtimes` in the returned aggregated data dict

## 4. TypeScript types — add runtime types

- [x] 4.1 Add `ModelRuntimeSummary` interface to `gitbench/web/src/lib/types.ts` with `total_ms`, `avg_ms`, `min_ms`, `max_ms`, `fixture_count`
- [x] 4.2 Add `model_runtimes: Record<string, ModelRuntimeSummary>` field to the `GitBenchData` interface

## 5. RuntimeBarChart React component

- [x] 5.1 Create `gitbench/web/src/components/charts/RuntimeBarChart.tsx` as a horizontal Recharts bar chart
- [x] 5.2 Read runtime data from `data.model_runtimes`, convert ms to seconds, sort fastest-first
- [x] 5.3 Implement provider-colored bars using `getProviderColor()`, Y-axis custom ticks with `ProviderIcon` and truncated names
- [x] 5.4 Implement tooltip showing full name, total runtime (seconds + minutes), and average per-fixture time
- [x] 5.5 Add `ModelSelector` filter to the chart
- [x] 5.6 Add fallback handling: "No runtime data available" when no models have timing data
- [x] 5.7 Add provider legend below the chart card

## 6. Page integration — add chart to Overview

- [x] 6.1 Import `RuntimeBarChart` in `gitbench/web/src/pages/index.astro`
- [x] 6.2 Add `<RuntimeBarChart client:load />` in a "Runtime (Wall Clock)" section after Cost per Full Run
