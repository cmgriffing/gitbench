## 1. Characterize Existing Boundaries

- [x] 1.1 Add a runner-level `llm_judge` characterization test that asserts the exact fixture, output, diff, prompt, campaign context, evidence, and exhaustion classification passed through the current scorer path.
- [x] 1.2 Add failing runner-level tests proving expected outputs currently fail for `commit_squash`, `git_bisect`, `reflog`, and `stash_recovery` because benchmark scoring hooks are bypassed.
- [x] 1.3 Add failing runner-level tests proving stateful commands are not executed for `git_clean`, `submodule_usage`, `tag_management`, and `worktree_usage`.
- [x] 1.4 Add a parallel worktree lifecycle test that detects benchmark-instance or cleanup-state sharing between fixtures.

## 2. Restore Benchmark Evaluation

- [x] 2.1 Route `llm_judge` fixtures through the existing judge-aware runner scorer without changing its arguments or failure behavior.
- [x] 2.2 Route all non-judge fixtures through `Benchmark.score()` so custom scorers and stateful command execution run.
- [x] 2.3 Instantiate isolated benchmark lifecycles for concurrently submitted fixtures while preserving sequential behavior and fixture ordering.
- [x] 2.4 Update `WorktreeUsageBenchmark.setup_fixture()` to accept the fixture-generation context and pass it to `GitExecutor`.

## 3. Correct Failure Classification

- [x] 3.1 Add a typed or otherwise explicit path for unsupported scoring configuration and benchmark lifecycle failures to reach runner classification.
- [x] 3.2 Mark setup, fixture-generation, and scoring-framework failures as infrastructure outcomes while retaining structured-output validation as a quality failure.
- [x] 3.3 Add campaign conversion and aggregation tests proving framework failures are excluded and make campaigns incomplete.

## 4. Verify Affected Benchmarks

- [x] 4.1 Add expected-answer and wrong-answer runner tests for the five reported benchmarks in text mode.
- [x] 4.2 Add runner coverage for `branch_cleanup`, `git_clean`, `submodule_usage`, and `tag_management` to prevent false passes from initial repository state.
- [x] 4.3 Verify representative custom and stateful fixtures in JSON-schema mode after canonicalization.
- [x] 4.4 Run the focused benchmark, runner, scorer, campaign, and structured-output test suites.
- [x] 4.5 Run a local mock smoke campaign across all nine affected benchmarks with multiple trials and both output modes.
- [x] 4.6 Document the affected result window and ensure regenerated results use a distinguishable benchmark-suite version without rewriting prior raw evidence.
