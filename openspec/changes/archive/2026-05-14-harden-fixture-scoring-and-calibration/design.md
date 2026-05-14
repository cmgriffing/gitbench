## Context

GitBench has 204 YAML fixtures across 17 benchmark suites. The current scoring model is mixed:

- Generic `similarity`, `exact_match`, `state_assertions`, and `structured` scoring live in `gitbench/harness/scorer.py`.
- Some benchmark suites add domain-specific scoring, such as `stash_recovery`, `reflog_recovery`, `bisect_regression`, `commit_selection`, and branch cleanup selection.
- Command-operation suites such as `submodule_usage`, `worktree_usage`, `tag_management`, and `git_clean` execute model output before checking state assertions.
- Read-only command fixtures often rely on `exact_match`, which rejects valid equivalent commands.

This creates two quality issues. Some fixtures are too brittle, such as requiring `git submodule` when `git submodule status` is also valid. Other fixtures are too permissive, especially conflict-resolution fixtures scored with broad string similarity thresholds.

## Goals / Non-Goals

**Goals:**

- Add a reusable command equivalence scorer that can be configured from fixture YAML.
- Keep command equivalence data explicit in fixtures rather than embedding broad Git semantics in scorer code.
- Normalize command strings enough to ignore insignificant formatting differences.
- Support both single-command and multi-command accepted alternatives.
- Tighten answer-selection scorers so extra incorrect selections can fail a fixture.
- Correct known bad or brittle fixtures and audit all suites for scoring and difficulty calibration.
- Preserve existing scoring behavior for fixtures that do not opt into new scorer types or stricter selection semantics.

**Non-Goals:**

- Building a full Git command semantic interpreter.
- Inferring arbitrary command equivalence automatically.
- Replacing state assertion scoring for operation fixtures.
- Changing model prompts except where a fixture is corrected or strengthened.
- Reworking report UI or historical result rendering.
- Changing fixture metadata fields added by the earlier fixture metadata change.

## Decisions

### Command equivalence is fixture-declared

Fixtures that accept equivalent commands will use a generic scorer with explicit accepted alternatives:

```yaml
scoring:
  type: command_equivalence
  accepted:
    - git submodule
    - git submodule status
```

For multi-command workflows, `accepted` can contain command sequences:

```yaml
scoring:
  type: command_equivalence
  accepted:
    - - git submodule init
      - git submodule update
    - - git submodule update --init
```

**Rationale:** Fixture authors know the intended equivalence class. Encoding those alternatives in YAML avoids a brittle hardcoded list of Git facts in the scorer and makes each fixture's accepted surface reviewable.

**Alternative considered:** Add named built-in equivalence groups such as `submodule_list`. Rejected for the first pass because it hides accepted behavior away from fixtures and creates a second registry to maintain. This can be added later if repetition becomes a problem.

### Normalize command tokens, not raw strings

The command equivalence scorer will normalize model output and accepted commands before comparison:

- Trim leading/trailing whitespace.
- Drop blank lines.
- Collapse equivalent shell spacing.
- Parse command lines with `shlex.split()` where possible.
- Compare token sequences rather than raw strings.

If `shlex.split()` fails for model output, the scorer will fail the fixture with a useful scoring error rather than falling back to loose string similarity.

**Rationale:** Small formatting differences should not affect correctness, but the scorer should still be strict about the command and arguments selected.

**Alternative considered:** Raw string comparison after whitespace normalization. Rejected because it still makes quoting and spacing differences unnecessarily brittle.

### Keep execution-based assertions separate

`command_equivalence` is for fixtures that ask for commands but do not need repo mutation to be validated. Operation fixtures that must prove repo state should continue to use `state_assertions` and benchmark-local command execution.

**Rationale:** Some Git commands are safe read-only answers, while others must be executed to prove they work. Combining equivalence and execution in one scorer would blur two different validation modes.

**Alternative considered:** Execute all command-equivalence outputs and compare effects. Rejected because read-only command fixtures often ask for the command itself, not its output, and because generic execution has safety and lifecycle concerns.

### Selection scoring should be exact by default

Selection-style scoring should require no missing expected items and no extra incorrect items unless a fixture explicitly opts into partial-credit behavior. Similarity can still be reported, but pass/fail must reflect exact set equality by default.

**Rationale:** In Git cleanup, commit selection, or branch selection tasks, including an extra branch or commit is usually a real error. Passing because all expected items were present hides dangerous over-selection.

**Alternative considered:** Keep current expected-coverage scoring and report extras only in the error. Rejected because it inflates pass rates and weakens benchmark validity.

### Calibration happens as an explicit audit

The implementation should audit every suite, not just the known failing examples. The audit should identify:

- Wrong expected values.
- Brittle exact matches with valid alternatives.
- Loose similarity thresholds that accept incomplete answers.
- Fixtures whose difficulty label no longer matches actual complexity.
- Suites with saturated stored pass rates that need harder variants or stronger assertions.

**Rationale:** Fixing only the submodule example would address one symptom but leave the benchmark uneven.

## Risks / Trade-offs

- **Risk:** Fixture authors may over-list accepted command alternatives and make tests too easy. → **Mitigation:** Document accepted alternatives as semantically equivalent only, and add tests that extras still fail.
- **Risk:** `shlex` tokenization does not model every shell behavior. → **Mitigation:** Treat tokenization as normalization, not execution semantics; fixtures with complex shell behavior should use state assertions instead.
- **Risk:** Tightening selection scoring may lower historical pass rates. → **Mitigation:** This is expected for better validity; document the scoring change and keep benchmark suite versioning intact.
- **Risk:** Full suite calibration can become large. → **Mitigation:** Start with known brittle/wrong fixtures and scorer primitives, then audit suite by suite with focused tasks.
- **Risk:** Command equivalence duplicates accepted alternatives across fixtures. → **Mitigation:** Keep the first implementation explicit; introduce named groups later only if real duplication appears.

## Migration Plan

1. Add the generic command equivalence scorer and tests.
2. Convert known command-equivalent fixtures, starting with submodule listing/status.
3. Correct known wrong expectations, starting with `git_show/f008`.
4. Tighten selection scorers and update tests for extra-answer failures.
5. Audit all suites and convert or strengthen fixtures where needed.
6. Run the full test suite and a mock benchmark run to verify all fixtures load and score.

Rollback is straightforward: fixtures can be restored to previous scoring types, and the new scorer is additive until fixtures opt into it.
