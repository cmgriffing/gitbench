## 1. Configuration

- [x] 1.1 Add `load_judge_config()` to `gitbench/config.py` that parses the optional `judge` section from config
- [x] 1.2 Add `--judge` CLI flag to `gitbench/cli.py` that enables judge scoring (overrides config)
- [x] 1.3 Add `--judge-profile` CLI flag to `gitbench/cli.py` to override the judge profile from config

## 2. Judge Client

- [x] 2.1 Create `gitbench/harness/judge.py` with `JudgeClient` class
- [x] 2.2 Implement `JudgeClient.__init__()` accepting a `ModelInterface` instance
- [x] 2.3 Implement `JudgeClient.evaluate_commit_message(diff, message)` with prompt construction, model call, and response parsing returning float
- [x] 2.4 Add retry logic in `evaluate_commit_message()` — one retry on failure

## 3. Scorer Integration

- [x] 3.1 Add optional `judge_client` parameter to `Scorer.__init__()`
- [x] 3.2 Modify `Scorer.score()` to use judge for `similarity` type when judge client is available and benchmark is judge-enabled
- [x] 3.3 Implement fallback in `Scorer.score()` — if judge fails after retry, use `SequenceMatcher` and set error on Score

## 4. Runner Wiring

- [x] 4.1 Add `judge_config` parameter to `BenchmarkRunner.__init__()`
- [x] 4.2 Create `JudgeClient` in `BenchmarkRunner.__init__()` when judge config is provided
- [x] 4.3 Pass `JudgeClient` to `Scorer` during construction
- [x] 4.4 Update `gitbench/cli.py` to create `BenchmarkRunner` with judge config

## 5. Commit Messages Benchmark

- [x] 5.1 Update `CommitMessagesBenchmark.score()` to store repo_path for diff access
- [x] 5.2 Ensure `get_diff()` is called before scoring and its output is available to the scorer/judge

## 6. Tests

- [x] 6.1 Create `tests/test_judge.py` with unit tests for `JudgeClient`
- [x] 6.2 Add mock judge tests — judge returns valid score, judge returns invalid response, judge fails
- [x] 6.3 Add judge integration tests to `tests/test_scorer.py` — scorer uses judge when configured, falls back when not
- [x] 6.4 Add CLI tests for `--judge` and `--judge-profile` flags
- [x] 6.5 Add integration test for end-to-end judge scoring of a commit_messages fixture

## 7. Documentation

- [x] 7.1 Update `README.md` with judge configuration documentation and usage examples
