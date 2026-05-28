## Context

GitBench currently has 204 fixtures across 17 benchmark suites. Recent stored results show four zero-pass fixtures, all in `git_log_format`, plus a low-pass cluster dominated by exact-match fixtures and broad similarity scoring. Inspection found several non-model-quality causes: order-sensitive multi-line exact matches, a prompt asking for a dynamic short hash while expecting a static commit message, merge-count setup that likely fast-forwards instead of creating merge commits, grep fixture setup/count mismatches, and conflict prompts where the desired resolution policy is not explicit.

The existing scoring system already supports exact match, similarity, command equivalence, structured fields, state assertions, and benchmark-specific scorers. This change extends that pattern with more deterministic scorers and an audit path before considering any LLM-as-judge evaluation. LLM-as-judge is explicitly out of scope for this change.

## Goals / Non-Goals

**Goals:**

- Correct the known zero-pass and suspicious low-pass fixture defects.
- Add deterministic scorers for unordered lists, numeric answers, dynamic commit-hash answers, and semantic structured values.
- Migrate brittle exact-match fixtures to deterministic scorers where the answer shape allows it.
- Add fixture self-checks so future fixture defects are caught before a full model run.
- Recalibrate difficulty labels after scoring and fixture corrections using observed pass-rate bands plus manual review.

**Non-Goals:**

- Introduce LLM-as-judge scoring.
- Make hard fixtures easy or remove useful expert-level coverage.
- Rewrite the whole benchmark suite or change result storage formats beyond normal score output fields.
- Treat historical results as directly comparable after fixture/scoring behavior changes.

## Decisions

### Prefer deterministic scorers over LLM judging

Use programmatic scoring for answer classes with objective correctness: sets of lines, numeric counts, commit hashes, JSON-like structured values, command alternatives, and repository state. This keeps runs reproducible, inexpensive, and debuggable.

Alternative considered: add LLM-as-judge for low-pass fixtures. Rejected for this change because the identified failures have concrete programmatic fixes and judge scoring would hide fixture defects instead of correcting them.

### Add small scorer types instead of one generic fuzzy scorer

Introduce narrowly scoped scoring types:

- `unordered_line_set` for order-insensitive lists.
- `numeric_exact` for integer/count answers with whitespace/prose normalization.
- `commit_hash_by_subject` for dynamic hash answers where the expected subject is stable but the hash changes per setup.
- `json_semantic_equal` or equivalent structured-value scoring for JSON conflict outputs.

Alternative considered: loosen exact-match thresholds or use similarity. Rejected because similarity can pass wrong answers and still fails deterministic variants such as reversed valid lists.

### Use self-checks to validate fixtures against actual repository state

Fixture self-checks should execute setup, derive benchmark context, and verify that the expected answer is consistent with the generated repository. They should catch static hashes, impossible merge counts, overwritten setup files, and multi-line exact matches that are likely order-sensitive.

Alternative considered: rely on full model runs to reveal fixture problems. Rejected because full runs are slow, costly, and conflate fixture defects with model behavior.

### Recalibrate difficulty after corrections

Difficulty labels should be updated only after correcting fixture/scoring defects. Observed pass rates should inform labels, but manual review remains necessary so a fixture is not marked harder merely because it was previously broken.

Alternative considered: immediately relabel based on current pass rates. Rejected because current pass rates include known fixture defects.

## Risks / Trade-offs

- Deterministic scorers may accidentally accept over-broad answers -> Keep scorer semantics narrow and add tests for extra/missing/incorrect values.
- Fixture corrections will break comparability with existing result files -> Bump the benchmark suite version and document the calibration change.
- Self-checks can become benchmark-specific -> Start with generic checks and add suite-specific checks only where the answer cannot be derived generically.
- Prompt clarifications may make some fixtures easier -> Clarify output contract and resolution policy without revealing the answer.
