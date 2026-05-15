## Context

The `PassRateBarChart` on the home page renders a vertical bar chart using Recharts. Currently:
- Height = `max(300, modelCount * 80)` — tall with many models
- Bar fill = green/yellow/red based on pass rate thresholds
- X-axis ticks use -40° rotated `foreignObject` at `y=-12`, centering labels on the axis line
- `ProviderIcon` renders simple-icons at size=12 with `color="default"` — some brand colors (Anthropic #191919, Meta #0866FF) have poor contrast against the dark `--card` background (#0f1520)

The chart lives on `index.astro` as a `client:load` React island.

## Goals / Non-Goals

**Goals:**
- Reduce chart height to a fixed ~350px, letting bars scale narrower
- Encode provider identity in bar color instead of pass rate
- Position X-axis labels below the axis line
- Make provider icons visible against dark background
- Add a provider color legend below the chart

**Non-Goals:**
- Changing the chart orientation (stays vertical bars)
- Refactoring chart layout beyond the scope listed
- Adding a new charting library (stays Recharts)
- Tooltips, hover states, or interactive features
- Modifying other charts (CostValueChart, BenchmarkHeatmap, TimeSeriesChart)

## Decisions

### Decision 1: Fixed chart height at 350px

`chartHeight = 350` (constant). The existing `barSize` formula already adapts:
```js
barSize = Math.max(12, Math.min(28, 400 / Math.max(1, chartData.length)))
```
With 40 models, bars hit the 12px floor — adequate for visual distinction. The Y-axis (0–100%) stays readable at any reasonable height. Bottom margin reduced from 80 to ~60 since labels fan downward with less vertical spread.

**Alternatives considered:**
- Cap at 500px: still too tall with 20+ models.
- Horizontal layout: cleaner labels but a larger visual redesign and the user preferred keeping vertical bars.

### Decision 2: Provider color palette

Hand-picked colors for known providers, deterministic hue fallback for unknowns:

```ts
const PROVIDER_COLORS: Record<string, string> = {
  anthropic: '#D97757',  // warm terracotta
  google:    '#4285F4',  // Google Blue
  meta:      '#0668E1',  // Meta blue (brightened for dark bg)
  mistral:   '#F59E0B',  // warm amber
  openai:    '#10A37F',  // OpenAI green-teal
  deepseek:  '#4F46E5',  // indigo
  xai:       '#E5E7EB',  // light gray
};

function getProviderColor(provider: string): string {
  return PROVIDER_COLORS[provider.toLowerCase()]
    ?? `hsl(${providerHue(provider)}, 55%, 48%)`;
}
```

The existing `providerHue()` in ProviderIcon.tsx provides the fallback hue. Colors are chosen for distinctiveness and contrast on the dark background. The `getColor(passRate)` function is replaced entirely.

**Alternatives considered:**
- Full deterministic palette: less aesthetically pleasing, no brand recognition.
- Pastel/light palette: lower contrast on dark bg, harder to distinguish.
- Keep pass-rate colors but add pattern/texture: overcomplicates the visual.

### Decision 3: Label offset — y=6 instead of y=-12

In `CustomXAxisTick`, the `foreignObject` positioning changes:
```diff
- y={-12}
+ y={6}
```
The height stays 32. After `rotate(-40°)`, the text fans downward and rightward from the tick anchor. This, combined with bottom margin reduction to 60, keeps labels fully visible.

### Decision 4: Icon visibility — two-tier approach

1. **For Anthropic specifically**: The simple-icons default `#191919` is near-black. Override to the provider palette color (`#D97757`) in the tick labels. Do this by detecting the provider in the tick renderer and rendering ProviderIcon with an explicit color for Anthropic.

2. **For all dark-brand-color icons**: In `ProviderIcon`, detect if the simple-icons default color has low relative luminance against the dark background. If below a threshold (~0.15), render a subtle `rgba(255,255,255,0.08)` circle behind the icon. This catches both Anthropic (#191919 → luminance ~0.01) and Meta (#0866FF → luminance ~0.07).

The implementation approach for detection: since simple-icons components set color via a `color` prop and we don't programmatically know the brand color from the component, the simplest approach is to hardcode a set of known-dark provider slugs (`['anthropic']`) for the color override, and apply the background circle universally for all 12-14px icons (it's nearly invisible on bright icons anyway).

Alternatively, we could maintain a luminance lookup table for known providers. But the universal circle approach is simpler and sufficient.

**Decision**: Apply a universal subtle background circle for all ProviderIcon instances rendered at sizes ≤14px within the chart tick labels. No luminance detection needed.

### Decision 5: Provider legend

A row of colored dots with provider names, rendered below the chart card:

```
● Anthropic  ● Google  ● Meta  ● Mistral  ● OpenAI  ● DeepSeek
```

Only providers present in the currently displayed models are shown. Each dot uses the same `getProviderColor()` function for consistency. The legend is a simple flexbox row with mono font at 10px, positioned between the chart card and the ModelSelector (or below the card, depending on what fits).

## Risks / Trade-offs

- **Small bars hide differences**: With 40 models at 12px bar width, visual differences between adjacent scores are subtle. → Mitigated by the provider color giving a second encoding channel; exact values available in tooltip/text.
- **Provider overlap**: Two providers with similar hues (e.g., Meta blue vs Google blue) could be confused. → The chosen palette deliberately spaces hues apart; the fallback uses golden-angle spacing which maximizes distinction.
- **Fixed height on mobile**: 350px might be tall on small screens. → The Recharts `ResponsiveContainer` handles width; height is fine since the chart is percentage-based.
- **Icon background circle on bright icons**: The circle is rgba(255,255,255,0.08), nearly invisible on bright icons — acceptable tradeoff for simplicity.

## Open Questions

- Should the legend appear above or below the chart card? Below the card seems cleaner (separates controls from data).
- Should we also add provider colors to the ModelSelector dropdown? Out of scope for this change but worth noting as a future enhancement.
