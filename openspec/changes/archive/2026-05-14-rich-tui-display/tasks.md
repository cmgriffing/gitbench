## 1. Setup and dependencies

- [x] 1.1 Add `rich>=13.0.0` to `pyproject.toml` dependencies
- [x] 1.2 Create `gitbench/ui/format.py` with `human_readable()`, `human_readable_cost()`, `format_duration()` functions
- [x] 1.3 Write unit tests for `format.py` in `tests/test_format.py`

## 2. Core RichProgressDisplay class

- [x] 2.1 Create `gitbench/ui/display.py` with `RichProgressDisplay` class skeleton implementing `RunProgress` protocol
- [x] 2.2 Implement `__init__`: state dicts, Rich `Console(stderr)`, `Live(screen=True, auto_refresh=False)`, initial layout
- [x] 2.3 Implement `model_started`, `benchmark_started`, `fixture_finished`, `benchmark_finished`, `model_finished` callbacks updating internal state and calling `_refresh()`
- [x] 2.4 Implement `_build_layout()`: header, per-model panels (horizontal split), comparison table, optional log panel
- [x] 2.5 Implement per-model panel rendering (`_render_model_panel`): progress bar, current benchmark, fixture progress, pass rate (color-coded), tokens (human-readable with ⇣/⇡), cost
- [x] 2.6 Implement comparison table rendering (`_render_summary_table`): rows fill live, "running"/"..." for in-progress/pending, delta column for 2+ models, color thresholds
- [x] 2.7 Implement `close()`: stop Live, print final static summary to stdout via Rich Console, print output file paths

## 3. Verbose mode integration

- [x] 3.1 Add `collections.deque`-based ring buffer (maxlen=500) for verbose log lines
- [x] 3.2 Implement `_render_log_panel()`: last 6 lines shown in fixed-height panel (only when `verbose=True`)
- [x] 3.3 Implement log file dump on `close()`: write full buffer to `gitbench-logs/verbose-{timestamp}.log`, print path to stderr

## 4. Non-TTY fallback

- [x] 4.1 Detect non-TTY stderr in `__init__`, set `self.enabled = False`
- [x] 4.2 When disabled, progress callbacks write plain-text status lines to stderr (no ANSI, no alternate screen)
- [x] 4.3 Final summary still renders to stdout if stdout is a TTY

## 5. Wire into CLI

- [x] 5.1 Update `gitbench/ui/__init__.py`: export `RichProgressDisplay`, remove old exports
- [x] 5.2 Update `cli.py` imports: replace `TerminalProgressTable`/`SummaryTable` with `RichProgressDisplay`
- [x] 5.3 Replace `TerminalProgressTable(...)` construction with `RichProgressDisplay(...)` in `run` command
- [x] 5.4 Remove `SummaryTable(...)` call and its rendering logic (now integrated into `RichProgressDisplay.close()`)
- [x] 5.5 Keep `_progress_model_names_for_runs` helper in `cli.py` (or move to `display.py`)
- [x] 5.6 Remove `announce_model` function (progress display handles initial state)

## 6. Clean up old code

- [x] 6.1 Delete `gitbench/ui/terminal.py`
- [x] 6.2 Delete `gitbench/ui/progress.py`
- [x] 6.3 Delete `gitbench/ui/summary.py`

## 7. Update tests

- [x] 7.1 Remove `TestTerminalProgressTable` class from `tests/test_cli.py`
- [x] 7.2 Remove `TestShouldUseColors` class from `tests/test_cli.py`
- [x] 7.3 Remove `TestSummaryTable` class from `tests/test_cli.py`
- [x] 7.4 Add `TestRichProgressDisplay` class to `tests/test_cli.py` covering: TTY detection, state transitions, panel content, summary table, verbose log, non-TTY fallback
- [x] 7.5 Update any CLI integration tests that reference deleted modules
- [x] 7.6 Run full test suite, verify all tests pass

## 8. Integration validation

- [x] 8.1 Run `gitbench run -a` with `--verbose` against mock models, verify live display renders correctly
- [x] 8.2 Pipe stderr (`2>&1 | cat`), verify non-TTY fallback works
- [x] 8.3 Verify JSON/JSONL output is unchanged from pre-change behavior
- [x] 8.4 Verify `gitbench report` still works with output from the new display
