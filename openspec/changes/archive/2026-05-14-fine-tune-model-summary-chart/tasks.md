## 1. Provider color palette

- [x] 1.1 Define `PROVIDER_COLORS` map and `getProviderColor()` function in a shared location (e.g., `lib/provider-colors.ts` or inline in PassRateBarChart.tsx)
- [x] 1.2 Reuse existing `providerHue()` from ProviderIcon.tsx for deterministic fallback

## 2. PassRateBarChart changes

- [x] 2.1 Replace `getColor(passRate)` with `getProviderColor(provider)` for bar `Cell` fills
- [x] 2.2 Change `chartHeight` from `Math.max(300, chartData.length * 80)` to constant `350`
- [x] 2.3 Adjust `bottomMargin` from 80 to ~60 to match reduced label spread
- [x] 2.4 In `CustomXAxisTick`, change `foreignObject` `y` from `-12` to `6` so labels fan below axis
- [x] 2.5 Add provider legend below chart card — horizontal flex row of colored dots + provider names for unique providers in displayed data

## 3. ProviderIcon visibility improvements

- [x] 3.1 For Anthropic provider: override `color="default"` to use the Anthropic palette color (`#D97757`)
- [x] 3.2 For icons ≤14px: add a background circle (`rgba(255,255,255,0.08)`) behind the icon SVG
- [x] 3.3 Pass the new `provider` prop through to ProviderIcon in `CustomXAxisTick` so it can apply the Anthropic override

## 4. Verification

- [x] 4.1 Run `npm run build` to confirm no build errors
- [ ] 4.2 Visually verify bar colors correspond to providers, not scores
- [ ] 4.3 Verify chart height is reasonable at 5, 15, and 30 model counts
- [ ] 4.4 Verify labels are below the axis line, not straddling it
- [ ] 4.5 Verify Anthropic icon is visible (terracotta, not black)
- [ ] 4.6 Verify provider legend appears and matches displayed providers
