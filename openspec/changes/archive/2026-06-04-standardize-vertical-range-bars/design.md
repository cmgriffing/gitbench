## Context

The Overview page has four grouped metric charts: pass rate, cost, runtime, and token usage. Each chart groups model efforts under provider/base-model IDs and already computes `minValue`, `maxValue`, and `representativeValue` for each group.

The current rendering uses `range` as the bar value for grouped charts. In Recharts this produces floating min-to-max bars: the visible mark begins at the lowest effort value and ends at the highest effort value. That does show spread, but it hides the absolute comparison against zero. It is especially confusing on pass rate, where a high-scoring model with a narrow range looks like a short bar near the top of the chart.

PassRateBarChart already uses the desired vertical orientation and diagonal X-axis labels. CostValueChart, RuntimeBarChart, and TokenUsageChart use horizontal range bars with Y-axis labels. This change makes the metric charts share one visual grammar.

## Goals / Non-Goals

**Goals:**

- Use vertical bars for pass rate, cost, runtime, and token usage.
- Keep the existing diagonal provider-icon X-axis labels from PassRateBarChart.
- Draw provider-colored bars from zero to `representativeValue`.
- Draw effort spread separately as neutral range whiskers from `minValue` to `maxValue`.
- Anchor all grouped metric numeric axes at zero.
- Preserve the current grouping, filtering, provider coloring, click navigation, tooltip, and sort direction semantics.

**Non-Goals:**

- Change report API payloads, SQLite schema, benchmark generation, or model grouping semantics.
- Change ScatterPlot, QuadrantComparisonChart, BenchmarkHeatmap, or TimeSeriesChart visualizations.
- Introduce a new charting dependency.
- Interpret effort ranges as statistical confidence intervals.

## Decisions

### Share One Grouped Metric Chart Renderer

Create a shared grouped metric chart renderer or helper layer for vertical charts rather than editing four components independently. The wrappers remain metric-specific for loading data, sorting, formatting axis ticks, tooltips, empty states, and section placement, but the shared renderer owns the common chart language:

- vertical Recharts bar layout
- category X-axis with `VerticalGroupTick`
- numeric Y-axis starting at zero
- provider-colored representative bars
- neutral range whiskers
- provider legend
- click-through behavior to the provider/base-model detail page

Alternative considered: patch each chart separately. That is lower upfront work, but it preserves duplication in axis setup, bar sizing, label spacing, and whisker behavior. Since the request is explicitly for one visual language across charts, the shared renderer reduces drift.

### Bars Represent Representative Values, Not Ranges

Each visible solid bar uses `representativeValue` as its data value:

- pass rate: median deduped effort score, higher is better
- cost: median deduped effort cost, lower is better
- runtime: median deduped effort runtime, lower is better
- tokens: median deduped effort token total, lower is better

Representative values are computed from sorted unique effort values so duplicate efforts do not overweight the median. For example, effort values `[10, 10, 10, 20, 50]` use representative value `20` while the whisker still spans `10` to `50`.

The existing `minValue` and `maxValue` remain the effort spread for the group. The renderer SHALL NOT rely on the artificial single-effort `range` padding to make a visible bar; the bar itself provides visibility. If `minValue === maxValue`, the whisker may collapse or be omitted while the representative bar remains visible.

Alternative considered: keep range bars and add a faint zero baseline fill. That would make absolute value somewhat visible, but it still asks users to decode two overlapping bar concepts. Separating bar and whisker is clearer.

### Whiskers Show Effort Spread

Render whiskers as neutral line-and-cap marks from `minValue` to `maxValue` in the same numeric scale as the bar. The UI copy and specs should call them "range whiskers", not "error bars", because they are effort-level ranges and not uncertainty estimates.

The implementation can use Recharts `ErrorBar` with asymmetric relative offsets or a custom SVG overlay shape. If Recharts `ErrorBar` creates z-index, hover, or cap-size problems on bars, use a custom shape/overlay so the visual stays deterministic.

### Numeric Domains Start at Zero

All grouped metric charts use numeric Y-axis domains with lower bound `0`.

- Pass rate uses `[0, 100]` unless a future metric explicitly requires a different percent ceiling.
- Cost, runtime, and token usage use `[0, paddedMax]`, where `paddedMax` is based on `maxValue` so the whisker caps fit.

The existing padded domain helper can be updated or wrapped so `floor: 0` means "anchor the lower bound at zero" for these charts, not only "do not go below zero."

### Keep Existing Diagonal X-axis Labels

All grouped metric charts use the current `VerticalGroupTick` pattern:

- provider icon
- truncated base model name
- `-40` degree rotation
- tick labels offset below the axis

This preserves the current overview chart affordance and avoids introducing a new label style for the converted cost, runtime, and token charts.

## Risks / Trade-offs

- Vertical charts can crowd with many selected groups -> keep the current selector-driven filtering, fixed chart height, dynamic bar sizing, and diagonal labels; verify the default selected set and a larger selected set by screenshot.
- Lower-is-better vertical charts invert the intuitive "taller is better" reading -> preserve best-first sorting and use tooltips/section labels to make metric direction clear.
- Whiskers may be hard to see against provider colors or grid lines -> use a neutral foreground stroke with sufficient opacity and cap size, and render above the bars.
- Recharts range/error primitives may include whisker values in domain calculations unexpectedly -> explicitly compute domains from `maxValue` with zero lower bound.
