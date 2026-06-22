## Context

`BenchmarkRunner` currently constructs a judge-aware `Scorer` and sends every fixture directly to it. That preserves fixture-driven LLM-judge routing, but bypasses the `Benchmark.score()` contract used by custom scoring types and by benchmarks that must execute model commands before state assertions. Separately, `worktree_usage` overrides `setup_fixture()` with an older signature and stores its current executor on the benchmark instance, which is unsafe when one instance is shared by parallel fixture workers.

The regression repair must be narrow because `llm_judge` campaign behavior includes distinct cache-key, evidence, and exhaustion semantics that are already implemented in the runner/scorer path.

## Goals / Non-Goals

**Goals:**

- Restore custom and stateful benchmark evaluation through `Benchmark.score()`.
- Preserve the current `llm_judge` scorer call and all arguments passed to it.
- Restore deterministic setup for `worktree_usage`.
- Avoid sharing mutable benchmark instances across parallel fixture lifecycles.
- Exclude scoring-framework failures from model-quality denominators.
- Add runner-level coverage that exercises real fixture lifecycles.

**Non-Goals:**

- Change judge prompts, ensemble averaging, caching, or evidence formats.
- Add campaign-scoped judge cache wiring or modify judge provenance.
- Redesign all benchmark scoring signatures around a new context object.
- Recalibrate fixture prompts or expected answers.

## Decisions

### Use explicit judge and benchmark evaluation paths

For `scoring.type: llm_judge`, the runner will retain the current call to its judge-aware `Scorer`, including `repo_path`, diff, prompt, and campaign scoring context. All other fixtures will be evaluated through `benchmark.score()`.

This deliberately keeps judge routing fixture-driven while restoring the benchmark extension point. A new cross-cutting scoring-context abstraction was rejected because it would require mechanical signature changes across every benchmark and create unnecessary regression surface. Moving all custom behavior into the generic scorer was rejected because command execution and repository mutation are benchmark lifecycle behavior, not pure score comparison.

### Isolate benchmark instances per parallel fixture

Parallel fixture execution will not share a benchmark instance across fixture lifecycles. Each submitted fixture will receive a fresh instance of its registered benchmark class. Sequential execution may continue to use one instance because fixture lifecycles do not overlap.

This avoids the existing `worktree_usage._current_executor` race without adding benchmark-specific parallelism flags. If construction later becomes expensive, an explicit stateless benchmark contract can be considered separately.

### Bring worktree setup back into the base contract

`WorktreeUsageBenchmark.setup_fixture()` will accept the keyword-only fixture generation context and pass it to `GitExecutor`. Its worktree and sibling cleanup registration remains benchmark-specific.

### Separate infrastructure failures from quality failures

Exceptions in fixture setup, context generation, scorer configuration, or benchmark evaluation that prevent a valid comparison will produce infrastructure outcomes. Provider responses that fail structured-output parsing or schema validation remain valid model-quality failures as required by campaign lifecycle specs.

Unsupported scoring configuration will fail preflight where practical; if encountered during execution it will still be classified as infrastructure rather than a model failure.

### Verify behavior at the runner boundary

Tests will use deterministic model outputs and real fixtures through `BenchmarkRunner`, not only direct calls to benchmark or scorer methods. Judge characterization tests will assert the exact scorer inputs and campaign failure classification before and after the dispatch change.

## Risks / Trade-offs

- [Risk] The explicit `llm_judge` branch leaves two evaluation paths in the runner. -> Mitigation: keep the branch keyed only by fixture scoring type and cover both paths with integration tests.
- [Risk] Fresh benchmark instances could lose runtime mutations applied to a shared instance. -> Mitigation: production configuration belongs in runner services or constructor defaults; add a parallel runner test before changing instantiation.
- [Risk] Re-enabled stateful benchmarks execute model-produced shell commands. -> Mitigation: preserve existing repository isolation, cleanup, timeouts, and command behavior without expanding accepted execution scope.
- [Risk] Historical reports contain false failures and some false passes. -> Mitigation: identify affected campaign versions and rerun affected benchmarks after deployment rather than rewriting raw evidence.

## Migration Plan

1. Add characterization tests for judge and benchmark dispatch.
2. Apply the dispatch, setup-contract, isolation, and classification fixes.
3. Run benchmark, runner, campaign, and structured-output suites.
4. Run a local smoke campaign covering one fixture from each affected benchmark in text and JSON-schema modes.
5. Mark June 17-20 affected benchmark aggregates as invalid for comparison and regenerate them with the corrected suite version.

Rollback is a code revert; regenerated results must remain distinguishable by benchmark-suite version and must not be merged with affected results.

## Open Questions

- Whether result publication needs an explicit invalidation marker in addition to benchmark-suite version separation.
