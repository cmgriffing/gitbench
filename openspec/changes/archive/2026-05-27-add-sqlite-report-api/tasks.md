## 1. Database Artifact

- [x] 1.1 Choose and document the Node SQLite dependency for Vercel/local API functions.
- [x] 1.2 Add `gitbench/web/data/schema.sql` with tables for models, runs, benchmarks, fixtures, fixture results, tags, summaries, runtimes, and base-model groups.
- [x] 1.3 Add indexes for model result, benchmark result, fixture detail, tag filter, run history, model grouping, and benchmark summary queries.
- [x] 1.4 Implement a Python database writer that rebuilds `gitbench/web/data/gitbench.db` from aggregated report data using the latest schema.
- [x] 1.5 Update `gitbench report` so it always writes the SQLite report database before build/preview.
- [x] 1.6 Add tests that verify report generation creates the database, replaces stale data, and preserves current aggregate counts.

## 2. Report Store

- [x] 2.1 Define typed report view models for summary, model list, model results, benchmark detail, fixture detail, and history responses.
- [x] 2.2 Define the `ReportStore` interface used by API route handlers.
- [x] 2.3 Implement `NodeSqliteReportStore` for Vercel/local functions with lazy connection caching.
- [x] 2.4 Keep SQL simple and adapter-contained so a future D1 implementation can satisfy the same store contract.
- [x] 2.5 Add store-level tests for summary, benchmark, model filter, fixture detail, and not-found queries.

## 3. Vercel API Routes

- [x] 3.1 Add Vercel API route structure for summary, models, model results, benchmark details, fixture details, and history.
- [x] 3.2 Add parameter and query validation with clear 400 responses for unsupported filters.
- [x] 3.3 Return 404 responses for missing models, benchmarks, and fixtures.
- [x] 3.4 Ensure summary/list endpoints exclude full `model_output` text.
- [x] 3.5 Configure Vercel function bundling so `gitbench.db` is available to deployed API routes.
- [x] 3.6 Add API route tests or integration checks for successful responses and error responses.

## 4. Web Client Migration

- [x] 4.1 Add a shared browser report client that calls `/api/*` endpoints and exposes view-specific loader functions.
- [x] 4.2 Migrate overview charts and selectors from `loadData()` to summary/model API payloads.
- [x] 4.3 Migrate compare page charts from `loadData()` to compact API payloads.
- [x] 4.4 Migrate benchmark detail interactive tables from full-data fetches to benchmark-scoped API payloads.
- [x] 4.5 Migrate model result galleries to model-scoped API payloads where client-side filtering needs API data.
- [x] 4.6 Remove or demote browser use of `/results.json` so it is no longer the canonical React island data source.

## 5. Local Development

- [x] 5.1 Add or document a `vercel dev` based local development command for API-backed report views.
- [x] 5.2 Ensure the static Astro build still works with `npm run build`.
- [x] 5.3 Ensure API-backed local development works after running `gitbench report`.
- [x] 5.4 Update README/report docs to explain the generated database, `vercel dev`, and compatibility role of `results.json`.

## 6. Verification

- [x] 6.1 Run Python tests covering report aggregation and database generation.
- [x] 6.2 Run web typecheck/build verification.
- [x] 6.3 Run API-backed local smoke checks for `/api/summary`, `/api/benchmarks/:benchmark`, `/api/models/:model/results`, `/api/fixtures/:benchmark/:fixture`, and `/api/history`.
- [x] 6.4 Verify browser network traffic no longer downloads the full `/results.json` for overview, compare, and benchmark interactive views.
- [x] 6.5 Run OpenSpec validation for `add-sqlite-report-api`.
