## ADDED Requirements

### Requirement: Judge failure handling preserves scoring consistency

LLM-judge scoring SHALL retry according to configured policy and SHALL mark the target attempt unscored if required judge results remain unavailable. It SHALL NOT fall back to a different scoring method within the campaign.

#### Scenario: A required judge remains unavailable

- **WHEN** judge retries are exhausted and the configured aggregate cannot be produced
- **THEN** the target attempt SHALL be marked unscored
- **AND** the campaign SHALL remain incomplete
- **AND** no heuristic fallback score SHALL enter campaign quality aggregates

### Requirement: Judge decisions are cached by campaign evidence identity

LLM-judge decisions SHALL be cached by fixture input hash, target output hash, and judge configuration hash within a campaign.

#### Scenario: Identical output is judged again

- **WHEN** the same fixture input, target output, and judge configuration recur in the campaign
- **THEN** the scorer SHALL reuse the cached judge decision
- **AND** it SHALL not issue duplicate judge calls

#### Scenario: Judge configuration changes

- **WHEN** any judge model, prompt, aggregation rule, or request configuration changes
- **THEN** the prior cached decision SHALL not be reused

### Requirement: Judge member evidence is auditable

The result store SHALL retain member-level judge scores, aggregation outcome, model/provider provenance, and failure state for each judged attempt.

#### Scenario: Inspect a judged fixture

- **WHEN** a user opens raw evidence for an LLM-judged attempt
- **THEN** each judge member result and the final aggregation SHALL be available subject to publication safety rules
