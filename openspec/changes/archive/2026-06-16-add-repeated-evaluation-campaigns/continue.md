# Continue — add-repeated-evaluation-campaigns

## Last action

Completed section 2 (tasks 2.1–2.5 / OpenSpec IDs 6–10): deterministic fixture inputs.

Evidence:
- `gitbench/utils/git.py` now has `FixtureGenerationContext` and passes stable Git author/committer/date/tz/locale env to all commands.
- `gitbench/harness/benchmark.py` `setup_fixture()` accepts an optional `fixture_generation_context`.
- `gitbench/harness/campaign.py` has provenance hash helpers, `FixtureExpectedHashes`, `expected_fixture_hashes` on `CampaignConfig`, and `Campaign.validate_attempt()` / `classify_attempts()` for hash-mismatch rejection.
- New tests in `tests/test_git.py` and `tests/test_campaign.py` verify deterministic commit/reflog identity and hash validation.
- `pytest tests/test_git.py tests/test_campaign.py -q` → 43 passed.
- `openspec/changes/add-repeated-evaluation-campaigns/tasks.md` checkboxes updated.

## Next action

Implement section 3: campaign runner, scheduling, resume, and storage.

1. Read `gitbench/harness/runner.py` and the `run` command in `gitbench/cli.py` to decide where to inject campaign orchestration.
2. Add `gitbench/harness/scheduler.py` to build numbered trial schedules and balanced ordering from `CampaignConfig`.
3. Add `gitbench/harness/store.py` to persist `campaign.json` and per-identity raw-attempt envelopes atomically under `gitbench-results/<campaign-id>/`.
4. Wire `--campaign-id` and `--trial-count` into the CLI and update live progress display.
5. Add the integration tests required by task 3.8.

## Why

The data model and deterministic hashing from section 2 are only useful once the runner can plan, persist, resume, and repair campaigns. The CLI `run` command is the natural integration point, but it is large, so this needs a focused session.

## Open threads

- No campaign scheduler/store exists yet (search confirmed no `CampaignScheduler` / `CampaignStore`).
- Section 3 tasks (3.1–3.8) are not started; section 4+ remain untouched.
- Existing runner still produces single-trial `BenchmarkResult` envelopes; campaign output will need to coexist with or wrap those.

## Do not

- Do NOT change the default behavior of non-campaign runs until campaign scheduling is fully wired and tested.
- Do NOT modify the web/report side (sections 6–9) before the Python runner and store are solid.
- Do NOT delete the existing per-model result envelope code; campaign output should build on it.
