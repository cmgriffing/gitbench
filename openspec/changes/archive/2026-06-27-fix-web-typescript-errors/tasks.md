## 1. Baseline and Shared Types

- [x] 1.1 Run `pnpm exec astro check --minimumSeverity error` from `gitbench/web` and confirm the current error classes before editing.
- [x] 1.2 Replace stale `@/types` imports with the existing `@/lib/types` module or local `./types.ts` imports.
- [x] 1.3 Import or re-export shared `FixtureResult` from the canonical type source so React components do not import non-exported local types from `report-store`.
- [x] 1.4 Remove incompatible optional redeclarations from chart metric interfaces, including `MetricEffort.reasoningLevel`.

## 2. API and Chart Contracts

- [x] 2.1 Add explicit response types for `loadModelResults`, including model results, campaign id, and campaign metadata.
- [x] 2.2 Add or reuse campaign-aware summary/chart data types for loaders and chart props that consume `campaign_id` and `campaign_metadata`.
- [x] 2.3 Align `availableOutputModes` typing across `useSyncedModelSelection`, `ModelOutputControls`, `OutputModeSelector`, and chart consumers.
- [x] 2.4 Rerun `pnpm exec astro check --minimumSeverity error` and record remaining errors after shared contract fixes.
  - Remaining after shared contract fixes: 57 errors in Astro React props, sidebar/layout typing, and model detail inline scripts.

## 3. Astro React Component Props

- [x] 3.1 Convert `class` to `className` only on imported React components used in `.astro` files, including `Badge` and `Button`.
- [x] 3.2 Convert `class` to `className` on lucide React icons used from `.astro` templates.
- [x] 3.3 Preserve native Astro/HTML `class` attributes unchanged.

## 4. Astro Data and Inline Scripts

- [x] 4.1 Add narrow server-side types or casts for `Object.values`, `Object.entries`, and `.map()` call sites that still infer `unknown` or implicit `any` in Astro frontmatter.
- [x] 4.2 Type the responsive sidebar script so event targets are narrowed before accessing `checked`, `parentElement`, and ARIA attributes.
- [x] 4.3 Type the model detail page filter and output-mode scripts with helper return types, output-mode unions, DOM element guards, and any required `Window` global declaration.
- [x] 4.4 Preserve existing selectors, localStorage keys, URL parameter names, and custom event names while adding type safety.

## 5. Verification

- [x] 5.1 Run `pnpm exec astro check --minimumSeverity error` from `gitbench/web` and ensure it exits successfully with zero errors.
- [x] 5.2 Run full `pnpm exec astro check` from `gitbench/web` and ensure it has no error-level diagnostics.
- [x] 5.3 Run `npm run build` from `gitbench/web` and ensure the production build succeeds.
- [x] 5.4 Review the diff to confirm no intentional route, report API, chart interaction, fixture page, navigation, or visual design behavior changed.
