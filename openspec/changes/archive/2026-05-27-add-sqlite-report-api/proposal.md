## Why

The Astro report currently makes browser islands fetch the full `results.json`, which is already nearly 29 MB raw and will keep growing as more models and runs are added. Most report views only need summaries, matrix data, or filtered fixture rows, so shipping every full model output to every chart is the wrong data boundary.

GitBench should move report reads behind query-shaped API endpoints backed by a generated SQLite database. This keeps the Astro UI static, supports local development through `vercel dev`, and creates a storage/query abstraction that can later migrate to Cloudflare D1 without rewriting the report UI.

## What Changes

- Generate a read-only SQLite report database as part of `gitbench report`.
- Store the report database at a stable web project path such as `gitbench/web/data/gitbench.db`, not an ephemeral directory.
- Rebuild the report database from the latest repository schema whenever report data is regenerated; existing report data may be dropped and recreated.
- Add Vercel API routes that query the generated SQLite database for summary, benchmark, model, fixture, and history data.
- Add a report-store abstraction so Vercel/local Node SQLite access and future Cloudflare D1 access share the same query contract.
- Update React islands to load query-specific API payloads instead of fetching the full `/results.json`.
- Keep the Astro app statically rendered and use `vercel dev` for local API-backed development.
- Keep compatibility JSON only as needed during transition; the API/database path becomes the canonical report data path.

## Capabilities

### New Capabilities

- `report-query-api`: Vercel API routes and generated SQLite report database for query-shaped report data access.

### Modified Capabilities

- `astro-site`: React report islands no longer rely on fetching the full static `/results.json` payload for interactive charts and tables.

## Impact

- `gitbench/render.py`: Add database generation from aggregated report data.
- `gitbench/cli.py`: Ensure `gitbench report` always writes the report database before build/preview.
- `gitbench/web/data/`: Add checked-in schema and generated database output location.
- `gitbench/web/api/`: Add Vercel API routes for report queries.
- `gitbench/web/src/lib/`: Add report client and report-store abstractions.
- `gitbench/web/src/components/charts/`: Replace full-data fetches with endpoint-specific client calls.
- `gitbench/web/package.json`: Add local development script for `vercel dev` if needed.
- Dependencies: Add a Node-compatible SQLite reader for Vercel/local functions, while keeping a separate D1 adapter path for future Cloudflare deployment.
