## ADDED Requirements

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
