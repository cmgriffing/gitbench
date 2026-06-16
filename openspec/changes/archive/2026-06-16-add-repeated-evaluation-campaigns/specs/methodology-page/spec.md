## ADDED Requirements

### Requirement: Methodology explains benchmark reliability metrics

The methodology page SHALL explain that model generation can be non-deterministic, describe evaluation campaigns and complete trial rounds, define mean one-attempt success and `pass_any_at_n`, explain stable-pass/flaky/stable-fail classifications, and state all denominator and exclusion rules.

#### Scenario: Reader interprets mean success

- **WHEN** a reader views a model with 80% mean success over five trials
- **THEN** the methodology SHALL explain that this is the proportion of valid attempts that passed
- **AND** it SHALL not describe it as the probability of passing at least once in five attempts

#### Scenario: Reader interprets excluded failures

- **WHEN** an attempt is absent because of provider, fixture-identity, or judge failure
- **THEN** the methodology SHALL explain that the campaign is incomplete
- **AND** the failure is not silently counted as model-quality failure

#### Scenario: Reader views a legacy campaign

- **WHEN** a report contains a one-trial legacy campaign
- **THEN** the methodology SHALL explain that fixture stability cannot be inferred from it

### Requirement: Methodology explains remaining sources of variance

The methodology page SHALL describe deterministic fixture inputs, target-provider routing evidence, LLM-judge caching and provenance, structured-output validation, and the limits of reproducibility.

#### Scenario: Reader assesses reproducibility

- **WHEN** a reader reviews the methodology
- **THEN** it SHALL avoid claiming that hosted model evaluations are deterministic
- **AND** it SHALL identify which inputs are fixed and which external factors can still vary

### Requirement: Methodology distinguishes resource normalizations

The methodology page SHALL distinguish mean per-trial cost, tokens, and API time from total campaign consumption and from wall-clock duration.

#### Scenario: Reader compares campaign costs

- **WHEN** two campaigns have different trial counts
- **THEN** the methodology SHALL explain why ranking charts use mean cost per complete trial
- **AND** why total campaign cost remains operationally relevant

