## Why

The web UI currently fails Astro's TypeScript checker with 97 errors, which makes build health hard to trust and hides real regressions behind known noise. This needs to be fixed before additional dashboard work so future UI, chart, and report API changes can rely on a clean typecheck gate.

## What Changes

- Fix stale type imports and shared data contracts so web UI code imports the existing `src/lib/types.ts` definitions consistently.
- Add explicit client/API response types where campaign-aware report endpoints and model-results loaders currently leak `unknown`.
- Align chart output-mode props so shared controls and chart pages agree on one representation.
- Correct React component props used from Astro templates, especially `className` for React islands and lucide icons.
- Add DOM narrowing and function parameter types to inline Astro browser scripts.
- Preserve existing dashboard behavior and visual output; this is a type-safety and build-health change, not a UI redesign.

## Capabilities

### New Capabilities
- `web-ui-typecheck`: Covers the web UI's TypeScript/Astro checker contract and the requirement that dashboard code remains typecheck-clean after these fixes.

### Modified Capabilities

None.

## Impact

- Affected code: `gitbench/web/src/lib`, `gitbench/web/src/components`, `gitbench/web/src/components/charts`, `gitbench/web/src/components/fixtures`, and selected `gitbench/web/src/pages` Astro files.
- Affected validation: `pnpm exec astro check --minimumSeverity error`, full `pnpm exec astro check`, and `npm run build` from `gitbench/web`.
- No new runtime dependencies are expected.
- No breaking API or dashboard behavior changes are intended.
