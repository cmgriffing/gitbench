## ADDED Requirements

### Requirement: Raw attempts record actual judge identity
Every campaign attempt evaluated by an LLM judge SHALL record the decision-complete judge configuration hash used for that evaluation. The judge hash SHALL be distinct from the generic scorer configuration hash.

#### Scenario: Judged attempt is persisted
- **WHEN** judge scoring produces a decision or exhausted evidence
- **THEN** raw attempt provenance SHALL contain the judge configuration hash reported by the judge evidence
- **AND** it SHALL not substitute the scorer configuration hash

#### Scenario: Non-judge attempt is persisted
- **WHEN** an attempt does not invoke an LLM judge
- **THEN** its provenance MAY omit judge configuration identity

### Requirement: Judge cache evidence is persisted before attempt completion
A newly produced judge decision SHALL be durably stored in the campaign cache before the corresponding raw attempt is marked complete.

#### Scenario: Process stops after judging
- **WHEN** judge evaluation finishes and the process stops after cache persistence but before the campaign completes
- **THEN** resume SHALL be able to reuse the persisted judge evidence
