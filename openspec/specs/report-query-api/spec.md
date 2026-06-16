# report-query-api Specification

## Purpose
TBD - created by archiving change add-sqlite-report-api. Update Purpose after archive.
## Requirements
### Requirement: Report generation writes SQLite database
`gitbench report` SHALL write a read-only SQLite report database at a stable path under the web project, using the latest repository schema as the source of truth.

#### Scenario: Report writes database artifact
- **WHEN** `gitbench report` completes successfully
- **THEN** the web project contains a generated SQLite database for report API queries

#### Scenario: Existing database is rebuilt
- **WHEN** `gitbench report` runs and a previous generated report database exists
- **THEN** the previous report data is replaced with data generated from the current benchmark results and latest schema

### Requirement: Report database schema supports queryable report data
The report database SHALL normalize models, runs, benchmarks, fixtures, fixture results, tags, model summaries, benchmark summaries, runtime summaries, and base-model group data enough to serve report views without parsing `results.json`.

#### Scenario: Summary data is queryable
- **WHEN** the report database is generated
- **THEN** model summaries, benchmark matrix values, runtime summaries, run metadata, and base-model group data can be read from database tables

#### Scenario: Fixture output data is queryable
- **WHEN** the report database is generated
- **THEN** prompts, expected outputs, setup commands, and model outputs can be queried for an individual fixture

### Requirement: Report database includes indexes for common access paths
The report database SHALL include indexes for common report access patterns, including fixture results by model and benchmark, fixture results by benchmark and fixture, fixtures by benchmark, fixture tags by tag and fixture, runs by model and timestamp, models by provider/base model/reasoning level, and benchmark summaries by model and benchmark.

#### Scenario: Indexes are present
- **WHEN** the generated database schema is inspected
- **THEN** indexes exist for model result, benchmark result, fixture detail, tag filter, run history, and model grouping queries

### Requirement: Vercel API routes expose query-shaped report data
The web project SHALL expose Vercel API routes that return report data for summary, models, model results, benchmark details, fixture details, and history.

#### Scenario: Summary endpoint returns compact data
- **WHEN** a client requests the summary API endpoint
- **THEN** the response includes the data needed for overview charts, selectors, benchmark matrix, runtime summaries, run metadata, and base-model groups
- **AND** the response does not include full model output text

#### Scenario: Benchmark endpoint returns benchmark-scoped data
- **WHEN** a client requests the benchmark API endpoint for a benchmark
- **THEN** the response includes benchmark metadata, tag counts, model leaderboard data, and per-fixture comparison rows for that benchmark

#### Scenario: Model results endpoint supports filters
- **WHEN** a client requests model results with benchmark, difficulty, or tag filters
- **THEN** the response includes only matching fixture result rows for that model

#### Scenario: Fixture endpoint returns full outputs
- **WHEN** a client requests the fixture detail API endpoint for a benchmark and fixture id
- **THEN** the response includes fixture metadata, prompt, expected output, setup commands, and all model outputs for that fixture

### Requirement: API uses report-store abstraction
API route handlers SHALL access report data through a report-store abstraction rather than embedding storage-specific database logic directly in UI components or route handlers.

#### Scenario: Node SQLite store serves Vercel routes
- **WHEN** Vercel API routes run locally or in production
- **THEN** they read the generated SQLite database through a Node SQLite report-store implementation

#### Scenario: Store contract allows D1 adapter
- **WHEN** a future Cloudflare D1 store is implemented
- **THEN** it can satisfy the same report-store contract used by the Vercel API routes

### Requirement: Local API-backed development uses Vercel dev
The supported local development path for API-backed report views SHALL use `vercel dev` so the static Astro app and Vercel API routes run together.

#### Scenario: Local API routes are available
- **WHEN** a developer starts the web project with the API-backed local development command
- **THEN** Astro pages and `/api/*` report routes are available from the local development server

### Requirement: API validates report query parameters
Report API routes SHALL validate route parameters and query parameters before executing database queries.

#### Scenario: Unknown fixture returns not found
- **WHEN** a client requests a fixture detail that does not exist
- **THEN** the API returns a 404 response

#### Scenario: Invalid filter is rejected
- **WHEN** a client passes an unsupported filter parameter to a report API endpoint
- **THEN** the API returns a clear 400 response

### Requirement: Report database stores fixture API duration
The report database SHALL store fixture-level `api_duration_ms` values in fixture result rows. The existing `model_runtimes` table SHALL store API-time aggregate values produced by aggregation, not wall-clock fixture durations.

#### Scenario: Fixture API duration is stored
- **WHEN** the report database is generated from aggregate data containing a fixture result with `api_duration_ms=350.2`
- **THEN** the corresponding `fixture_results` row stores `api_duration_ms=350.2`

#### Scenario: Missing API duration remains null
- **WHEN** the report database is generated from aggregate data containing no `api_duration_ms` for a fixture result
- **THEN** the corresponding `fixture_results.api_duration_ms` value is null
- **AND** `duration_ms` is not copied into `api_duration_ms`

#### Scenario: Runtime summary table stores API-time totals
- **WHEN** aggregate data contains `model_runtimes[model].total_ms=1200.0`
- **THEN** the generated `model_runtimes` row stores `total_ms=1200.0` as API-time data

### Requirement: Report APIs expose API-time runtime data
Report APIs SHALL expose fixture-level `api_duration_ms` on fixture result payloads where fixture result rows are returned. Summary and chart APIs SHALL continue returning `model_runtimes`, with values representing API-time aggregates.

#### Scenario: Summary endpoint returns API-time runtime summaries
- **WHEN** a client requests the summary API endpoint
- **THEN** the response includes `model_runtimes` values representing API call latency aggregates

#### Scenario: Model results endpoint returns fixture API duration
- **WHEN** a client requests model results for a model with fixture API timing data
- **THEN** each matching fixture result includes `api_duration_ms`

#### Scenario: Fixture endpoint returns fixture API duration
- **WHEN** a client requests fixture detail for a fixture with model outputs
- **THEN** each output with API timing data includes `api_duration_ms`

### Requirement: Report database stores output mode
The report database SHALL store `output_mode` for runs, model summaries, runtime summaries, benchmark summaries, and fixture result rows. Database access paths SHALL distinguish text and JSON-schema result variants for the same model.

#### Scenario: Result rows include output mode
- **WHEN** the report database is generated from aggregate data containing `output_mode=json_schema`
- **THEN** the corresponding fixture result rows store `json_schema` as their output mode

#### Scenario: Summary rows do not merge modes
- **WHEN** text and JSON-schema results exist for the same model
- **THEN** summary and benchmark rows keep separate aggregates for each output mode

### Requirement: Report APIs expose output mode filters
Report APIs SHALL expose output mode on returned model, run, benchmark, and fixture result payloads. APIs that return result rows SHALL accept an optional `output_mode` filter where mode filtering is meaningful.

#### Scenario: Model results filtered by output mode
- **WHEN** a client requests model results with `output_mode=json_schema`
- **THEN** only JSON-schema fixture results are returned for that model

#### Scenario: Fixture detail returns all modes
- **WHEN** a client requests fixture detail for a fixture that has text and JSON-schema outputs
- **THEN** the response includes both outputs and identifies each output's mode

#### Scenario: Unsupported output mode is rejected
- **WHEN** a client requests a report API with an unsupported `output_mode` value
- **THEN** the API returns a 400 response with a clear error

### Requirement: Report database stores structured-output payload fields
The report database SHALL store structured-output raw response text, parsed payload JSON, and structured-output error text for fixture results where those values exist.

#### Scenario: Structured payload is queryable
- **WHEN** a fixture result contains a parsed structured payload
- **THEN** fixture detail API responses can include that payload for debugging and display

#### Scenario: Compact endpoints omit bulky structured fields
- **WHEN** a summary, benchmark, or compact model-results endpoint returns fixture result rows
- **THEN** bulky raw structured output and full parsed payload data are omitted unless the endpoint is explicitly fixture-detail scoped

### Requirement: Report storage persists campaign entities

The report database SHALL persist campaigns, trials, raw fixture attempts, fixture aggregates, model and benchmark campaign summaries, resource summaries, judge evidence, and publication state with referential integrity.

#### Scenario: Build a report database

- **WHEN** campaign result artifacts are ingested
- **THEN** each raw attempt SHALL be associated with exactly one campaign and trial
- **AND** aggregate rows SHALL retain their source campaign identity

### Requirement: Campaign-sensitive queries accept an explicit selector

Report-store methods and HTTP endpoints that return benchmark results SHALL accept a campaign selector and SHALL include the selected campaign's status in the response.

#### Scenario: Query a model in a selected campaign

- **WHEN** a client requests model results with a campaign ID
- **THEN** only results and aggregates from that campaign SHALL be returned

#### Scenario: Omit campaign selection

- **WHEN** a client omits the campaign selector
- **THEN** the API SHALL select the latest completed publishable campaign
- **AND** it SHALL return the resolved campaign ID

### Requirement: Raw attempt queries are bounded

The API SHALL expose raw attempts through exact-identity or paginated queries and SHALL not embed all raw outputs in aggregate responses.

#### Scenario: List attempts for a fixture aggregate

- **WHEN** a client requests attempts for one fixture, model, effort, and output mode
- **THEN** the API SHALL return a bounded page with trial identities and attempt evidence

### Requirement: Public queries enforce publication safety

Public report queries SHALL exclude raw attempts that have not reached an allowed safety state when campaign safety review is required.

#### Scenario: Query an unpublished attempt

- **WHEN** a public client requests an attempt whose safety state is pending or blocked
- **THEN** the API SHALL not return its raw prompt or output content

### Requirement: Report database persists exact campaign identities
The report database SHALL persist campaign raw attempts and exact campaign summaries with campaign ID, trial index, model name, reasoning level, output mode, benchmark name, and fixture ID. Primary keys and indexes SHALL prevent collisions between reasoning efforts or output modes for the same model and fixture.

#### Scenario: Same model in two reasoning efforts
- **WHEN** a campaign contains attempts for the same model and fixture at `low` and `high` reasoning
- **THEN** both attempts SHALL be stored without collision
- **AND** exact lookup SHALL return only the requested reasoning effort

#### Scenario: Same fixture in two output modes
- **WHEN** a campaign contains text and JSON-schema attempts for the same fixture
- **THEN** summary and raw-attempt rows SHALL keep both output modes separate
- **AND** campaign denominators SHALL NOT merge the modes unless the response names the result as a rollup

### Requirement: Campaign-sensitive APIs return campaign data
Report-store methods and HTTP endpoints that accept a campaign selector SHALL read campaign tables and return campaign-derived metrics for the selected campaign, not legacy one-shot rows with campaign metadata attached.

#### Scenario: Query selected campaign model results
- **WHEN** a client requests model results with a campaign ID, model, reasoning effort, and output mode
- **THEN** the response SHALL contain only attempts or aggregates from that selected campaign and exact variant
- **AND** the response SHALL include selected campaign status and denominator metadata

#### Scenario: Omit campaign selection
- **WHEN** a client omits campaign selection
- **THEN** the API SHALL select the latest completed publishable campaign when one exists
- **AND** otherwise it SHALL select the latest incomplete campaign with incomplete status visible

### Requirement: Raw attempt APIs require exact identity or bounded pagination
Raw-attempt APIs SHALL either page through attempts with explicit bounds or address one attempt by exact identity. Exact identity SHALL include trial index, model name, reasoning level, output mode, benchmark, and fixture ID.

#### Scenario: Exact raw-attempt lookup
- **WHEN** a client requests one raw campaign attempt by exact identity
- **THEN** the API SHALL return at most one attempt
- **AND** it SHALL return 404 when any identity dimension does not match

#### Scenario: Paginated raw-attempt listing
- **WHEN** a client lists raw attempts for a campaign fixture
- **THEN** the API SHALL apply a bounded limit and offset
- **AND** each row SHALL include trial, model, reasoning level, output mode, status, score, resource usage, and safety state

### Requirement: Public raw content obeys publication safety
Campaign API routes SHALL NOT return raw prompt, model output, structured raw output, parsed payload, or judge rationale for attempts that are unpublished, pending safety review, or blocked.

#### Scenario: Pending safety state
- **WHEN** a public client requests raw content for an attempt whose safety state is pending
- **THEN** the API SHALL omit raw content fields
- **AND** it SHALL still expose non-sensitive status and denominator metadata

