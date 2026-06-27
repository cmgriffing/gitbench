## Context

The web UI lives under `gitbench/web` and uses Astro 6, React 19, TypeScript 6, Vercel API handlers, and shared report data types from `src/lib/types.ts`. Running `pnpm exec astro check --minimumSeverity error` currently reports 97 TypeScript errors across 109 checked files.

The diagnostics cluster into a few root causes rather than 97 independent fixes:

- stale `@/types` imports even though the actual module is `@/lib/types`
- `loadModelResults` and campaign-aware API helpers returning untyped JSON, causing `unknown` in React consumers
- chart output-mode availability represented as `Set<string>` in hooks/selectors but `OutputMode[]` in the shared controls wrapper
- `MetricEffort` redeclaring an inherited required property as optional
- React components and lucide icons used in `.astro` templates with Astro/HTML `class` instead of React `className`
- inline browser scripts relying on untyped DOM `Element`, implicit `any` parameters, and undeclared `window` properties

The implementation should fix these root contracts first so the remaining errors shrink quickly and can be handled locally.

## Goals / Non-Goals

**Goals:**

- Make `pnpm exec astro check --minimumSeverity error` pass in `gitbench/web`.
- Keep full `pnpm exec astro check` free of errors; warnings and hints may be handled separately unless trivial.
- Keep `npm run build` passing after type fixes.
- Preserve existing dashboard UI, route behavior, report API response behavior, and chart interactions.
- Prefer existing type definitions and local helper APIs over new abstractions.

**Non-Goals:**

- Redesigning charts, pages, navigation, or visual styling.
- Changing report data generation, SQLite schema, or campaign selection semantics.
- Adding new dependencies.
- Reworking Astro inline scripts into React islands unless type narrowing proves impractical.
- Eliminating every warning or hint unrelated to failing errors, such as deprecated Recharts `Cell` hints.

## Decisions

### Use `src/lib/types.ts` as the source of truth

All UI-facing benchmark, fixture, campaign, and report data types should import from `@/lib/types` or relative `./types.ts`. Do not create a second `@/types` module or duplicate structural aliases just to silence errors.

Alternative considered: add a compatibility module at `src/types.ts`. That would hide stale imports but keep two apparent type entry points and make future drift more likely.

### Type API client responses at the client boundary

`getJson<T>` already supports typed JSON. The implementation should give `loadModelResults` and chart/summary loaders explicit response types, including campaign metadata where the API returns it.

Alternative considered: cast data at each component call site. That would remove local errors but preserve the underlying API contract ambiguity and require repeated casts in charts.

### Represent available output modes consistently as a `Set`

`useSyncedModelSelection` and `OutputModeSelector` already use `Set<string>` semantics because the UI needs membership checks. The shared `ModelOutputControls` prop should accept that same representation instead of converting to arrays at each chart.

Alternative considered: convert the hook to return `OutputMode[]`. That is workable, but it would push membership conversion into the selector or consumers and change the shape already used directly by `QuadrantComparisonChart`.

### Fix Astro React props locally, not by weakening component types

Astro HTML elements should keep `class`, while React components imported into `.astro` files (`Badge`, `Button`, lucide icons) should use `className`. Component prop types should remain idiomatic React types.

Alternative considered: widen `Badge` and `Button` props to accept `class`. That would mask incorrect React usage and would not help lucide icon types.

### Narrow DOM types inside inline scripts

Inline scripts should use `instanceof` checks, typed helper functions, and narrow `querySelectorAll` loops before accessing `.value`, `.dataset`, `.style`, or custom globals. This keeps the existing client-side behavior while satisfying strict TypeScript.

Alternative considered: mark scripts as unchecked or cast broadly to `any`. That would keep errors hidden and weaken the build gate this change is meant to restore.

## Risks / Trade-offs

- Shared type changes can reveal additional downstream errors after the first pass -> Run `astro check` after each root-cause batch and address newly exposed diagnostics in the same sequence.
- Campaign-aware data may be represented differently by summary, chart, model-results, and fixture endpoints -> Use small response interfaces per loader rather than overloading one broad type where endpoint shapes differ.
- React prop fixes in `.astro` templates are repetitive and easy to over-apply -> Only change imported React components and icons; do not touch native HTML attributes.
- Inline script narrowing can accidentally change runtime behavior if selectors are rewritten too aggressively -> Preserve selectors and branching, adding only type guards and defaults.

## Migration Plan

No data migration or deployment sequencing is required. The change is source-only and should be validated locally by installing locked dependencies, running Astro type checks, and building the web UI.

Rollback is a normal source revert of the OpenSpec implementation commit because no persistent data or API migration is involved.

## Open Questions

None currently. The implementation can proceed with the diagnostics captured from `astro check` as the acceptance baseline.
