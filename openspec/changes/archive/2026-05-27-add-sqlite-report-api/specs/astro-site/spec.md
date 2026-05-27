## MODIFIED Requirements

### Requirement: results.json served as static asset
The aggregated benchmark data MAY be written to `ui/public/results.json` by the Python CLI as a compatibility artifact. The Astro site SHALL NOT embed the full report data in page HTML. React islands SHALL load query-specific report data through the report API client instead of fetching the full `/results.json` payload.

#### Scenario: results.json is accessible when emitted
- **WHEN** the built site is served and compatibility JSON was emitted during report generation
- **THEN** `GET /results.json` returns the aggregated benchmark data as JSON

#### Scenario: results.json is gitignored
- **WHEN** checking the gitignore
- **THEN** `ui/public/results.json` and `ui/dist/` are listed

#### Scenario: React islands do not fetch full report payload
- **WHEN** a hydrated React chart or interactive table loads in the browser
- **THEN** it requests only the query-specific API payload needed for that view
- **AND** it does not fetch `/results.json` as the canonical report data source

### Requirement: Build produces static dist/ directory
Running `npm run build` in `gitbench/ui/` SHALL produce a static Astro site in `ui/dist/` with HTML, CSS, JS, and static assets. The Astro page output SHALL remain static, while API-backed report data SHALL be served by deployment-specific API functions during local development and hosted production.

#### Scenario: Build completes successfully
- **WHEN** `npm run build` is executed
- **THEN** `ui/dist/` contains `index.html`, subdirectories for routes, and static assets

#### Scenario: Static page output is deployable
- **WHEN** `ui/dist/` is served by a static file server
- **THEN** statically generated Astro routes and assets are accessible

#### Scenario: API-backed deployment provides report queries
- **WHEN** the app is served through the supported API-backed local or hosted deployment
- **THEN** static Astro pages can request `/api/*` report endpoints for interactive report data
