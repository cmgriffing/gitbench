## Context

GitBench runs LLM benchmarks by iterating over fixtures, calling a model API, and scoring the output. Currently the runner collects pass/fail counts, similarity scores, token usage, and cost — but not wall-clock time. The web UI displays pass rates, cost, and token usage in bar charts on the Overview page, but has no speed dimension.

Result data flows through: runner → JSON files → `render.py` aggregation → `web/public/results.json` → Astro site. The new runtime data needs to thread through every layer of this pipeline.

## Goals / Non-Goals

**Goals:**
- Capture per-fixture wall-clock time with minimal overhead and no impact on accuracy measurement.
- Persist timing in result JSON so historical runs can be re-analyzed.
- Aggregate timing per model and per benchmark in the render pipeline.
- Display a bar chart on the Overview page ranking models by total runtime (fastest first).

**Non-Goals:**
- Per-benchmark runtime comparison (single aggregated view per model is the starting point).
- Historical/trend runtime tracking (runs from different dates won't be averaged — each run stands alone).
- Sub-second profiling breakdowns (API call time vs. scoring time — out of scope).
- Adding runtime to fixture detail pages or model detail pages.

## Decisions

### 1. Measure wall-clock per fixture, not per benchmark

**Choice**: Wrap each fixture execution (`_run_fixture`) with `time.perf_counter()` rather than wrapping each benchmark or the entire model run.

**Rationale**: Per-fixture timing gives us maximum flexibility. We can compute per-benchmark totals or per-model totals by summing fixture times. Measuring at coarser granularity throws away data. The overhead of two `perf_counter()` calls per fixture is negligible (~microseconds) compared to multi-second model calls.

**Alternative considered**: Per-benchmark timing only. Rejected because it would hide variation between fixtures and prevent future drill-downs.

### 2. Store duration as milliseconds (`duration_ms`) in Score

**Choice**: Add an optional `duration_ms: float | None` field to the `Score` dataclass and persist it in result JSON under `scores[].duration_ms`.

**Rationale**: Milliseconds are a human-friendly unit for operations that take 1–30 seconds. Using seconds would require decimal fractions that are harder to scan. `None` handles errors and older data.

**Alternative considered**: Store as seconds (`duration_s`). Rejected because milliseconds avoid decimal clutter in the 100–30,000 range.

### 3. Add `model_runtimes` to aggregated JSON alongside `model_summaries`

**Choice**: Output a `model_runtimes` dict keyed by model name with `total_ms`, `avg_ms`, `min_ms`, `max_ms` fields, rather than extending `model_summaries` directly.

**Rationale**: Separating runtime from pass-rate summary keeps the data model clean. `model_summaries` already carries 7 fields; adding 4 more would bloat it. A parallel dict lets the runtime chart read exactly what it needs.

**Alternative considered**: Extend `model_summaries` with `total_runtime_ms`, etc. Rejected to avoid conflating two different dimensions in one struct.

### 4. New chart: horizontal bar chart, fastest first

**Choice**: A horizontal bar chart (like `CostValueChart` and `TokenUsageChart`) with Y-axis = model, X-axis = total runtime in seconds, sorted fastest→slowest (ascending).

**Rationale**: Horizontal bars are easier to label with model names (side-by-side with icon + truncated name). This is the established pattern from the cost and token usage charts. Sorting fastest-first follows user intuition — people scan for the fastest model at the top.

**Alternative considered**: Vertical bar chart (like `PassRateBarChart`). Rejected because rotated X-axis labels are harder to read with long model names.

### 5. Chart placement: after Cost per Full Run, before Token Usage

**Choice**: Insert the `RuntimeBarChart` section between "Cost per Full Run" and "Token Usage" on the Overview page.

**Rationale**: Logical ordering — pass rate → cost → runtime → token usage → benchmark matrix. Cost and speed are closely related (faster models often cost more or less depending on pricing model).

## Risks / Trade-offs

- **Old result files lack duration_ms**: The runner will only populate `duration_ms` for runs after this change. The aggregation and chart should handle absent data gracefully (skip models with no timing data, show "No runtime data" message if none exists). **Mitigation**: All fields default to `None`, aggregation skips nulls, chart shows a fallback message.
- **Parallel execution complicates timing**: With `fixture_workers > 1`, wall-clock time per fixture may include thread scheduling overhead. **Mitigation**: We measure per-fixture wall time regardless of parallelism. This is correct — users care about actual elapsed time for a model, not idealized sequential time.
- **Model API timeouts inflate runtime**: A fixture that times out will record its timeout duration as runtime. **Mitigation**: This is actually useful — timeout-prone models should rank slower, reflecting real-world reliability.

## Open Questions

- Should we measure model call time vs. scoring time separately? (Deferred — current scope is total fixture time.)
- Should the charts page support toggling between seconds/milliseconds? (Deferred — start with seconds in the chart, milliseconds in raw data.)
