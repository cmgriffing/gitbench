## ADDED Requirements

### Requirement: Runner honors benchmark-specific evaluation
The benchmark runner SHALL evaluate every non-`llm_judge` fixture through the selected benchmark's scoring hook. Benchmark-specific scoring types and benchmark-specific command execution SHALL occur before the final score is recorded.

#### Scenario: Custom selection scorer runs through the runner
- **WHEN** a `commit_squash` fixture declares `scoring.type: commit_selection` and the model identifies the expected commits
- **THEN** the runner SHALL use the benchmark's commit-selection scorer
- **AND** it SHALL NOT report the scoring type as unsupported

#### Scenario: Recovery scorer runs through the runner
- **WHEN** a `reflog` or `stash_recovery` fixture receives the expected recovery reference
- **THEN** the benchmark-specific recovery scorer SHALL determine the result

#### Scenario: Stateful commands execute before assertions
- **WHEN** a stateful fixture receives model commands that produce the expected repository state
- **THEN** the benchmark SHALL execute the commands in the fixture repository before state assertions run
- **AND** the fixture SHALL pass when all assertions succeed

### Requirement: Parallel fixture lifecycles are isolated
The runner SHALL NOT share mutable benchmark lifecycle state between concurrently executing fixtures.

#### Scenario: Worktree fixtures run with parallel workers
- **WHEN** multiple `worktree_usage` fixtures are scheduled concurrently
- **THEN** each fixture SHALL use an isolated benchmark lifecycle and executor reference
- **AND** cleanup for one fixture SHALL NOT target another fixture's worktrees

### Requirement: Benchmark setup overrides remain contract-compatible
Every benchmark setup override SHALL accept the deterministic fixture-generation context defined by the base benchmark contract and SHALL apply it to repository generation.

#### Scenario: Deterministic worktree fixture setup
- **WHEN** a campaign plans or executes a `worktree_usage` fixture with a fixture-generation context
- **THEN** setup SHALL complete without a signature error
- **AND** generated Git identities SHALL use that context
