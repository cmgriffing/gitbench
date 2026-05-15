## Why

The Model Summary bar chart on the home page uses chart height that scales linearly with model count (`chartData.length * 80`), producing absurdly tall charts as the benchmark suite grows. It also redundantly encodes pass rate in both bar height and bar color, while ignoring the more useful provider dimension. Finally, label positioning and icon contrast issues hurt readability on dark backgrounds.

## What Changes

- Chart height switches from `max(300, modelCount * 80)` to a fixed ~350px height. Bars scale narrower as model count grows, using the existing adaptive `barSize` formula.
- Bar fill colors change from pass-rate thresholds (green/yellow/red) to provider-specific colors using a hand-picked palette with deterministic hue fallback.
- X-axis tick labels are offset below the axis line (positive y instead of negative) so they fan downward after rotation instead of straddling the axis.
- ProviderIcon gains visibility improvements: Anthropic's near-black icon color is replaced with a warm terracotta from the provider palette, and dark brand-colored icons receive a subtle light background circle.
- A provider legend with small colored dots is rendered below the chart.

## Capabilities

### New Capabilities
- `provider-bar-colors`: Provider-specific color palette for bar chart fills, applied as a legend below the PassRateBarChart and used for icon visibility fallbacks.

### Modified Capabilities
- `chart-components`: **BREAKING spec changes** — `PassRateBarChart` requirement changes from dynamic height (`max(300, modelCount * 80)`) to fixed ~350px height; bar color changes from pass-rate thresholds to provider-specific colors; tick label offset moves from straddling to below-axis positioning.
- `provider-brand-icons`: ProviderIcon requirement changes to allow overriding simple-icons `color="default"` for visibility on dark backgrounds, either by substituting the provider palette color or adding a background circle for dark brand colors.

## Impact

- `gitbench/web/src/components/charts/PassRateBarChart.tsx` — bar color logic, chart height, label offset, legend rendering
- `gitbench/web/src/components/ProviderIcon.tsx` — icon color override and background circle logic
- `openspec/specs/chart-components/spec.md` — update PassRateBarChart requirements
- `openspec/specs/provider-brand-icons/spec.md` — update ProviderIcon requirements
- New: `openspec/specs/provider-bar-colors/spec.md` — provider palette spec
