## Why

The runner bypasses benchmark-specific scoring hooks, causing custom scoring types to fail as unsupported and preventing stateful benchmarks from executing model commands before checking repository state. Recent campaigns therefore record infrastructure defects as model failures, including zero-pass results across several otherwise viable benchmarks.

## What Changes

- Route non-judge fixture evaluation through each benchmark's scoring hook so benchmark-specific selection, recovery, and stateful command behavior executes.
- Preserve the current fixture-driven `llm_judge` path, including its judge-aware scorer, campaign context, evidence, and exhaustion semantics.
- Make `worktree_usage` fixture setup compatible with deterministic campaign fixture generation.
- Prevent stateful worktree evaluation from sharing mutable benchmark state across parallel fixtures.
- Classify benchmark setup and scoring infrastructure failures as non-quality outcomes rather than valid model failures.
- Add runner-level regression coverage using real custom-scored and stateful fixtures.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `fixture-scoring-robustness`: Require the runner to honor benchmark-specific scoring and command-execution behavior for existing fixture scoring types.
- `llm-judge-scoring`: Clarify that fixture-driven LLM-judge routing remains on the shared judge-aware scorer while non-judge fixtures retain benchmark-specific evaluation behavior.
- `campaign-execution-lifecycle`: Treat benchmark setup and scoring-framework failures as excluded infrastructure outcomes instead of model-quality failures.

## Impact

- Affects `gitbench/harness/runner.py`, the benchmark scoring contract, `worktree_usage` setup and parallel execution behavior, campaign attempt classification, and runner integration tests.
- Corrects results for `commit_squash`, `git_bisect`, `reflog`, `stash_recovery`, and `worktree_usage`, with additional impact on `branch_cleanup`, `git_clean`, `submodule_usage`, and `tag_management`.
- Does not change judge prompts, judge aggregation, judge caching, judge evidence schema, or persisted judge provenance.
