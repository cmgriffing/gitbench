## MODIFIED Requirements

### Requirement: Runner wires judge into benchmark execution
The `BenchmarkRunner` SHALL construct a single judge-aware `Scorer` when a judge is configured. Fixtures declaring `scoring.type: llm_judge` SHALL be evaluated by that scorer with the rendered diff, original prompt, and campaign scoring context. Non-judge fixtures SHALL retain benchmark-specific evaluation behavior and SHALL NOT invoke the judge.

#### Scenario: Runner with judge configuration
- **WHEN** the runner is initialized with a valid `judge` section and evaluates an `llm_judge` fixture
- **THEN** the runner's judge-aware `Scorer` SHALL receive the fixture, target output, rendered diff, original prompt, and campaign scoring context

#### Scenario: Non-judge benchmark with judge configuration
- **WHEN** the runner has a judge configured but evaluates a fixture with a benchmark-specific non-judge scoring type
- **THEN** the benchmark-specific scoring hook SHALL evaluate the fixture
- **AND** the judge SHALL NOT be called

#### Scenario: Runner without judge configuration
- **WHEN** the runner is initialized without a `judge` section
- **THEN** non-judge fixtures SHALL run through their benchmark-specific evaluation normally
- **AND** only `llm_judge` fixtures would error, normally prevented by preflight

#### Scenario: Campaign judge exhaustion remains unscored
- **WHEN** all judge models fail while the corrected runner dispatches a campaign `llm_judge` fixture
- **THEN** the attempt SHALL remain unscored with judge evidence
- **AND** it SHALL NOT be converted into a benchmark-specific or heuristic quality score
