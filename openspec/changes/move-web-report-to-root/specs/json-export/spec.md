## MODIFIED Requirements

### Requirement: CLI supports render --format json
The `gitbench render` CLI command SHALL support a `--format json` option that calls `render_json()` instead of `render_html()`. It SHALL accept `--output` to specify the output path, defaulting to `web/public/results.json`.

#### Scenario: render --format json writes JSON
- **WHEN** `gitbench render --format json --output web/public/results.json` is executed
- **THEN** the aggregated data is written as JSON to the specified path

### Requirement: CLI provides gitbench report command
The CLI SHALL provide a `gitbench report` command that aggregates legacy run results from `gitbench-results/`, ingests campaign artifacts from campaign directories containing `campaign.json`, validates configured result-safety publication requirements, and writes compatibility JSON to `web/public/results.json`. The command SHALL NOT run Astro build, dev-server, preview, or browser-opening workflows.

#### Scenario: report command publishes compatibility JSON
- **WHEN** `gitbench report` completes successfully
- **THEN** `web/public/results.json` contains the aggregated report JSON
- **AND** the command prints guidance for running web module commands when a user wants to build or view the report

#### Scenario: deprecated web flags do not run web workflows
- **WHEN** `gitbench report --open`, `gitbench report --dev`, or `gitbench report --no-build` is executed
- **THEN** the command prints a deprecation warning for the flag
- **AND** it does not run Astro build, dev-server, preview, or browser-opening behavior
- **AND** it still publishes compatibility JSON when valid report inputs are present

#### Scenario: report command ingests campaign artifacts
- **WHEN** `gitbench report` scans a result directory containing `campaign.json` and raw campaign attempt envelopes
- **THEN** the generated report JSON SHALL include campaign metadata, trials, exact raw-attempt references, fixture aggregates, and campaign summaries
- **AND** it SHALL NOT require a separate manual campaign export step
