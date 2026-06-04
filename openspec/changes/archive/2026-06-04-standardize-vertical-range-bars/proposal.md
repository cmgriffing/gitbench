## Why

The grouped overview charts currently mix two concepts in the same mark: the bar itself represents the min-to-max effort range, so high-performing groups can appear as short floating bars. This makes absolute metric values harder to compare and creates a different visual language between the Model Summary chart and the cost, runtime, and token charts.

## What Changes

- Standardize grouped metric charts on vertical bars across pass rate, cost, runtime, and token usage.
- Render the solid provider-colored bar from zero to the representative effort value.
- Compute the representative effort value as the median of the sorted, deduped effort values for the group.
- Render the effort spread separately as a neutral range whisker from the lowest effort value to the highest effort value.
- Keep the existing diagonal `-40` degree X-axis labels with provider icon and truncated base model text.
- Anchor grouped metric numeric axes at zero.
- Preserve existing sort directions: pass rate sorts higher representative scores first, while cost, runtime, and tokens sort lower representative values first.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `chart-components`: PassRateBarChart and shared overview chart conventions change from floating range bars to zero-based representative bars with range whiskers.
- `cost-value-chart`: CostValueChart changes from a horizontal range bar chart to the shared vertical representative-bar plus range-whisker chart language.
- `runtime-chart`: RuntimeBarChart changes from a horizontal range bar chart to the shared vertical representative-bar plus range-whisker chart language.
- `token-usage-chart`: TokenUsageChart changes from a horizontal range bar chart to the shared vertical representative-bar plus range-whisker chart language.

## Impact

- Affected code: `gitbench/web/src/components/charts/PassRateBarChart.tsx`, `CostValueChart.tsx`, `RuntimeBarChart.tsx`, `TokenUsageChart.tsx`, `grouped-chart-ui.tsx`, and potentially `model-groups.ts` if range/representative fields need adjustment.
- Affected specs: grouped chart rendering requirements for pass rate, cost, runtime, and token usage.
- No API, data schema, package dependency, or benchmark output format changes are expected.
