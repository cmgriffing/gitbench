## Context

The web report currently has two data paths:

- Astro pages call `loadDataSync()` during static generation and parse `public/results.json`.
- Hydrated React islands call `loadData()` in the browser, which fetches the full `/results.json`.

The current `results.json` in this workspace is about 28.9 MB raw. The `fixtures` field dominates the payload because it includes every model output for every fixture. Summary charts, selectors, comparison charts, and benchmark matrices usually need only compact summaries or pass/fail rows, so the browser downloads far more data than the active view needs.

The app should remain a static Astro site, but the hosted/development runtime can include Vercel API functions. Local API-backed development will use `vercel dev`.

## Goals / Non-Goals

**Goals:**

- Generate a stable read-only SQLite report database whenever `gitbench report` runs.
- Query report data through Vercel API routes instead of browser-fetching the entire results payload.
- Keep the Astro site statically built.
- Use `vercel dev` as the supported local development path for API-backed pages.
- Design the database schema and query layer so a future Cloudflare D1 adapter can reuse the same logical contract.
- Keep full `model_output` fields out of summary/list endpoints and only return them from detail endpoints that need them.

**Non-Goals:**

- Do not add a mutable production database.
- Do not implement Cloudflare deployment or D1 bindings in this change.
- Do not add schema migrations for generated local/Vercel report artifacts; rebuilding from the latest schema is sufficient.
- Do not remove all legacy JSON generation unless it is no longer needed by the CLI or transition path.

## Decisions

### Decision 1: Generated SQLite is the canonical report data artifact

`gitbench report` will write a SQLite database at a stable web project path such as `gitbench/web/data/gitbench.db`. The database is generated from the current aggregate report data, treated as read-only by the web app, and bundled into Vercel functions for production queries.

**Rationale:** GitBench report data is generated offline from benchmark results. A read-only SQLite artifact gives the API efficient filtering, indexing, and joins without introducing an external service. It also aligns with Cloudflare D1's SQLite model.

**Alternatives considered:**

- Keep one large `results.json`: rejected because the browser payload is already too large and will grow.
- Generate many static JSON shards: simpler hosting story, but weaker query abstraction and less useful for a future D1 migration.
- Use a hosted database: rejected because report data is generated and replaceable, not user-mutated runtime state.

### Decision 2: Latest schema wins for generated database rebuilds

The repository schema is the source of truth. Report generation may delete any existing generated database, create a fresh database from the latest schema, insert current report data, create indexes, and optionally run `ANALYZE`.

**Rationale:** The local/Vercel database is an output artifact, not durable user data. Supporting migrations for generated artifacts would add complexity without preserving anything valuable.

**Alternatives considered:**

- Versioned migrations for local/Vercel DB files: unnecessary for disposable generated data.
- In-place updates: unnecessary and more error-prone than a full rebuild.

### Decision 3: Vercel API routes provide the current query surface

Add API routes under the web project for:

- `GET /api/summary`
- `GET /api/models`
- `GET /api/models/:model/results`
- `GET /api/benchmarks/:benchmark`
- `GET /api/fixtures/:benchmark/:fixture`
- `GET /api/history`

Route names may be adjusted for Vercel filesystem routing, but the API surface should remain view-oriented and stable.

**Rationale:** Vercel functions let the Astro app remain static while providing query-shaped payloads. Local development can use the same routes through `vercel dev`.

**Alternatives considered:**

- Astro server or hybrid output: rejected for now because the static Astro build contract should remain intact.
- Direct browser SQLite access: rejected because it complicates bundle size and runtime compatibility, and still exposes storage details to the UI.

### Decision 4: ReportStore isolates runtime-specific database access

The API layer will call a `ReportStore` interface with methods such as:

- `getSummary()`
- `getModels()`
- `getBenchmark(name)`
- `getModelResults(model, filters)`
- `getFixtureOutputs(benchmark, fixture)`
- `getHistory()`

The initial implementation will be `NodeSqliteReportStore` for Vercel/local Node. A future `D1ReportStore` can implement the same contract.

**Rationale:** Node SQLite packages and Cloudflare D1 bindings have different APIs. Keeping route handlers behind a store interface avoids coupling UI/API contracts to one runtime.

**Alternatives considered:**

- Write SQL directly in every route: faster initially, but makes a D1 migration invasive.
- Build a generic ORM layer: unnecessary for a small read-only report schema.

### Decision 5: Summary endpoints exclude full outputs

The schema and API responses will separate compact result facts from large text fields. Summary, benchmark, model, chart, and selector endpoints return only fields needed for their views. Full prompts, expected outputs, and model outputs are returned only by fixture-detail style endpoints.

**Rationale:** The current payload problem is caused by shipping large text fields to views that do not render them. The API contract should prevent that regression.

### Decision 6: Index the read paths explicitly

The generated schema will include indexes for common access patterns:

- fixture results by model and benchmark
- fixture results by benchmark and fixture
- fixtures by benchmark
- tags by tag and fixture
- runs by model and timestamp
- models by provider, base model, and reasoning level
- benchmark summaries by model and benchmark

**Rationale:** Moving from a single static JSON fetch to API queries only helps if common routes are fast and predictable.

## Risks / Trade-offs

- **[Risk] Native SQLite dependency friction on Vercel** -> Mitigation: choose a Vercel-compatible Node SQLite package, keep database access isolated behind `NodeSqliteReportStore`, and document the supported Node runtime.
- **[Risk] Generated database is not bundled with functions** -> Mitigation: add Vercel function include configuration or colocate data where Vercel includes it reliably; verify in build/deploy tests.
- **[Risk] `npm run dev` no longer represents the full app** -> Mitigation: document `vercel dev` as the API-backed development command and optionally add `npm run dev:api`.
- **[Risk] API payloads drift from current component expectations** -> Mitigation: migrate through a shared client library so components depend on typed report view models, not raw endpoint details.
- **[Risk] Future D1 differences leak into current implementation** -> Mitigation: keep SQL simple, avoid Node-specific SQL extensions, and separate the store contract from the Node SQLite adapter.

## Migration Plan

1. Add the schema and database writer while leaving `results.json` generation intact.
2. Add `ReportStore`, Node SQLite adapter, and Vercel API routes.
3. Add a browser report client that calls the new API endpoints.
4. Migrate React islands from `loadData()` to endpoint-specific client calls.
5. Keep static Astro page generation on existing synchronous data loading until the generated pages are separately optimized.
6. Verify `gitbench report`, `npm run build`, and `vercel dev` all work with the generated database.
7. Once all browser islands use the API, treat `/results.json` as compatibility output rather than the canonical report read path.

Rollback is straightforward: keep the old `/results.json` generation and restore React islands to `loadData()` if the API path is not ready.

## Open Questions

- Which Node SQLite dependency should be used for Vercel compatibility and install reliability?
- Should the generated `gitbench.db` be committed for demos, ignored as a build artifact, or regenerated during every report/deploy flow?
- Should static Astro pages eventually read from SQLite during build, or continue using the in-memory aggregate data path?
