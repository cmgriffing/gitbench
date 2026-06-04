## 1. Shared Chart Rendering

- [x] 1.1 Add a shared vertical grouped metric chart renderer or helper in `gitbench/web/src/components/charts/grouped-chart-ui.tsx`.
- [x] 1.2 Make the shared renderer draw provider-colored solid bars from zero to `representativeValue`.
- [x] 1.3 Make the shared renderer draw neutral range whiskers from `minValue` to `maxValue`, with visible caps and no user-facing "error bar" terminology.
- [x] 1.4 Add or update a zero-anchored numeric domain helper so grouped metric Y-axes start at 0 and include each row's `maxValue`.
- [x] 1.5 Keep the existing `VerticalGroupTick` diagonal provider-icon label pattern for grouped metric X-axes.

## 2. Chart Conversions

- [x] 2.1 Update `PassRateBarChart` to use representative-value bars, range whiskers, and a 0-100 Y-axis.
- [x] 2.2 Update `CostValueChart` from horizontal range bars to vertical representative-value bars with cost range whiskers.
- [x] 2.3 Update `RuntimeBarChart` from horizontal range bars to vertical representative-value bars with runtime range whiskers.
- [x] 2.4 Update `TokenUsageChart` from horizontal range bars to vertical representative-value bars with token range whiskers.
- [x] 2.5 Preserve current sorting, model selection, provider legend, click navigation, empty states, tooltip content, and metric formatters in each chart.

## 3. Data Semantics

- [x] 3.1 Stop relying on artificial single-effort range padding for visible bars; single-effort groups remain visible via `representativeValue`.
- [x] 3.2 Ensure representative values use the median of sorted, deduped effort values while range whiskers span each group's min/max values.
- [x] 3.3 Ensure domains are computed from `maxValue` so range whiskers fit inside the chart.

## 4. Verification

- [x] 4.1 Run `pnpm test:api` from `gitbench/web`.
- [x] 4.2 Run `pnpm build` from `gitbench/web`.
- [x] 4.3 Use agent-browser against the local web app to screenshot the Overview page and verify all four grouped metric charts are vertical, zero-based, and use diagonal labels.
- [x] 4.4 Verify the default selected model set and a larger selected set do not produce overlapping chart labels or unreadable whiskers.
