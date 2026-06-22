# Benchmark Scoring Regression — Affected Result Window

## Summary

The benchmark runner bypassed benchmark-specific scoring hooks, causing custom
scoring types to fail as unsupported and preventing stateful benchmarks from
executing model commands before checking repository state. This affected
results recorded between **June 17–20, 2026** under benchmark-suite version
`0.3.0`.

## Affected Benchmarks

| Benchmark | Issue | Impact |
|---|---|---|
| `commit_squash` | `commit_selection` scoring type unsupported | Zero passes (false fails) |
| `git_bisect` | `bisect_regression` scoring type unsupported | Zero passes (false fails) |
| `reflog` | `reflog_recovery` scoring type unsupported | Zero passes (false fails) |
| `stash_recovery` | `stash_recovery` scoring type unsupported | Zero passes (false fails) |
| `worktree_usage` | Commands not executed; shared state in parallel | Zero passes; parallel corruption |
| `branch_cleanup` | `exact_match` selection not dispatched | Potential false passes |
| `git_clean` | Commands not executed | Potential false passes from initial state |
| `submodule_usage` | Commands not executed | Potential false passes from initial state |
| `tag_management` | Commands not executed | Potential false passes from initial state |

## Affected Result Directories

- `gitbench-results/20260619T231424Z/` — v0.3.0 results (June 19–20)
- `gitbench-results-bak/20260617T202311Z/` — v0.3.0 results (June 17)
- `gitbench-results-bak/20260616T192400Z/` — v0.3.0 results (June 16, partial)
- `gitbench-results-dirty/` — earlier v0.3.0 results (June 10–11, may also be affected)

## Remediation

- The scoring regression has been fixed in benchmark-suite version **0.3.1**.
- Regenerated results use version `0.3.1` and are distinguishable from affected
  `0.3.0` results.
- Prior raw evidence is **not** rewritten. Affected aggregates should be
  marked invalid for comparison.
- Rollback is a code revert; `0.3.1` results must not be merged with `0.3.0`
  results.