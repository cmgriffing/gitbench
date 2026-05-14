## Fixture Calibration Audit

This audit covers all 17 fixture suites for brittle expectations, loose scoring,
incorrect expected values, and difficulty calibration.

### blame_forensics

- Reviewed exact-match fixtures. No command-equivalence migration needed because
  prompts ask for commit subjects, not commands.
- Recent stored pass rate: 118/132 (0.894). Not saturated.

### branch_cleanup

- Tightened selection scoring so extra branches fail by default.
- Existing fixtures remain exact-match inputs but now score as strict sets.
- Recent stored pass rate: 77/132 (0.583). Not saturated.

### cherry_pick

- Raised conflict-resolution similarity thresholds from 0.5 to 0.9.
- Multi-file prompts already require filename-prefixed output where multiple
  returned files are expected.
- Recent stored pass rate: 132/132 (1.000). Strengthened by stricter scoring.

### commit_messages

- Reviewed similarity-based scoring. These fixtures intentionally allow natural
  language variation in concise commit messages, so no strict exact-match change
  was made.
- Recent stored pass rate: 107/132 (0.811). Not saturated.

### commit_squash

- Tightened commit selection scoring so clearly selected extra commits fail by
  default while target/base context remains allowed.
- Recent stored pass rate: 132/132 (1.000). Strengthened by stricter selection.

### git_bisect

- Reviewed dynamic commit scoring. Existing scorer resolves the target commit
  from the repo instead of relying on a brittle static hash.
- Recent stored pass rate: 131/132 (0.992). Near-saturated, but dynamic target
  scoring is already exact; no fixture correction was needed in this pass.

### git_clean

- Reviewed state assertions. Fixtures execute model commands and validate file
  state instead of command text, so command-equivalence migration is not needed.
- No recent April 28 stored baseline was available for this newer suite.

### git_grep

- Reviewed exact and high-threshold similarity fixtures. Existing exact matches
  are used where prompts request literal grep output.
- No recent April 28 stored baseline was available for all fixtures in this suite.

### git_log_format

- Reviewed exact-match command-output fixtures. Prompts ask for specific log
  formatted output, so exact matching remains appropriate.
- No recent April 28 stored baseline was available for all fixtures in this suite.

### git_show

- Corrected f008 to resolve and score the full hash for `Second commit` instead
  of expecting the literal subject.
- Other exact-match fixtures ask for literal metadata values and remain exact.

### merge_conflicts

- Raised conflict-resolution similarity thresholds from 0.5 to 0.9.
- Added regression coverage that resolving only one file in a multi-file fixture
  fails.
- Recent stored pass rate: 132/132 (1.000). Strengthened by stricter scoring.

### rebase

- Raised conflict-resolution similarity thresholds from 0.5 to 0.9.
- Multi-file prompts already explicitly scope expected output to one or two
  returned file contents as appropriate.
- Recent stored pass rate: 131/132 (0.992). Strengthened by stricter scoring.

### reflog

- Reviewed dynamic reflog scoring. The scorer resolves commit hashes from the
  fixture repo and exact-checks those hashes.
- Recent stored pass rate: 132/132 (1.000). Saturated, but no loose threshold or
  brittle static expectation was found in this pass.

### stash_recovery

- Reviewed stash-reference scoring. The scorer exact-checks stash refs and
  accepts refs embedded in commands.
- Recent stored pass rate: 131/132 (0.992). Near-saturated, but no loose threshold
  or brittle static expectation was found in this pass.

### submodule_usage

- Migrated f006 to `command_equivalence`, accepting both `git submodule` and
  `git submodule status`.
- Reviewed `.gitmodules` viewing and submodule status fixtures; exact matching
  remains appropriate where the prompt requests a specific file-view command or
  status command.
- Recent stored pass rate: 110/132 (0.833). Not saturated.

### tag_management

- Reviewed state assertions. Fixtures execute model commands and validate tag
  state, so command-equivalence migration is not needed.
- No recent April 28 stored baseline was available for this newer suite.

### worktree_usage

- Migrated the worktree listing fixture to `command_equivalence`, accepting
  `git worktree list` and `git worktree list --porcelain`.
- State-changing worktree fixtures remain state-assertion based.
- Recent stored pass rate: 119/132 (0.902). Not saturated.

## Saturation Summary

Stored April 28 results show saturated or near-saturated pass rates for
`cherry_pick`, `commit_squash`, `git_bisect`, `merge_conflicts`, `rebase`,
`reflog`, and `stash_recovery`. This implementation strengthens saturated
conflict-resolution suites by raising thresholds and strengthens saturated
commit-selection behavior by rejecting clear extra selections. No new fixtures
were added, so fixture metadata uniqueness and metadata completeness remain
unchanged by this audit.
