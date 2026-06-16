## MODIFIED Requirements

### Requirement: CLI provides gitbench report command
The CLI SHALL provide a `gitbench report` command that: (1) aggregates legacy run results from `gitbench-results/`, (2) ingests campaign artifacts from campaign directories containing `campaign.json`, (3) writes `gitbench/web/public/results.json`, (4) writes the generated SQLite report database, (5) runs `pnpm build` in `gitbench/web/` unless skipped, and (6) opens the built report or prints the path when requested.

#### Scenario: report command builds and opens
- **WHEN** `gitbench report --open` is executed
- **THEN** the Astro site is built to `gitbench/web/dist/`
- **AND** the dashboard page is opened through the supported preview flow

#### Scenario: report command skips build if --no-build
- **WHEN** `gitbench report --no-build` is executed
- **THEN** report JSON and SQLite data artifacts are written
- **AND** the Astro build step is skipped

#### Scenario: report command ingests campaign artifacts
- **WHEN** `gitbench report` scans a result directory containing `campaign.json` and raw campaign attempt envelopes
- **THEN** the generated report JSON SHALL include campaign metadata, trials, exact raw-attempt references, fixture aggregates, and campaign summaries
- **AND** it SHALL NOT require a separate manual campaign export step

## ADDED Requirements

### Requirement: Campaign JSON export uses unambiguous metrics
Campaign JSON export SHALL use `mean_success_rate`, `pass_any_at_n`, `planned_trials`, `completed_trials`, `valid_attempts`, `passing_attempts`, and `excluded_attempts` for campaign metrics. Campaign export SHALL NOT use `pass_at_k` as the headline campaign metric.

#### Scenario: Repeated campaign export
- **WHEN** a campaign with five planned trials is exported
- **THEN** the campaign JSON SHALL identify all five trials and their completion state
- **AND** fixture summaries SHALL expose passing and valid attempt counts
- **AND** model and benchmark summaries SHALL expose `mean_success_rate`

#### Scenario: Legacy artifact remains readable
- **WHEN** `gitbench report` ingests a historical one-shot result artifact
- **THEN** the legacy aggregate fields SHALL remain readable
- **AND** the report SHALL NOT infer repeated-trial stability from that artifact

### Requirement: Campaign JSON export preserves exact attempt identity
Every raw campaign attempt record or reference in JSON export SHALL include campaign ID, trial index, model ID, reasoning effort, output mode, benchmark, and fixture ID.

#### Scenario: Exact identity exported
- **WHEN** a raw attempt is exported for a JSON-schema high-reasoning model run
- **THEN** its exported identity SHALL include `campaign_id`, `trial_index`, `model_id`, `reasoning_effort`, `output_mode`, `benchmark`, and `fixture_id`
