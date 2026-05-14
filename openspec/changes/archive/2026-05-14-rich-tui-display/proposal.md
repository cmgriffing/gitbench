## Why

The current CLI output during `gitbench run` uses hand-rolled ANSI escape codes for a bare-bones plain-text progress table and a static post-run summary. It lacks visual hierarchy, progress bars, live comparative results across models, and human-readable token/cost formatting. Replacing this with a Rich-based TUI display gives a polished, consistent, information-dense live view that updates in-place as benchmark data arrives — making multi-model comparison immediate rather than something you only see in the post-run report.

## What Changes

- **Add `rich` as a required dependency** in `pyproject.toml`
- **Create `gitbench/ui/display.py`** with a `RichProgressDisplay` class implementing the existing `RunProgress` protocol, rendering a live alternate-screen display with per-model progress panels, a live comparison summary table, and an optional verbose log panel
- **Create `gitbench/ui/format.py`** with `human_readable()` and `human_readable_cost()` utilities for K/M/B token formatting
- **Delete `gitbench/ui/terminal.py`** — ANSI color codes, `should_use_colors()`, `is_output_suppressed()` are all replaced by Rich's built-in handling
- **Delete `gitbench/ui/progress.py`** — `TerminalProgressTable` is replaced by `RichProgressDisplay`
- **Delete `gitbench/ui/summary.py`** — `SummaryTable` is integrated into the live display, with a final static summary rendered on close
- **Update `cli.py`** to use `RichProgressDisplay` instead of `TerminalProgressTable` + `SummaryTable`
- **Update tests** to cover `RichProgressDisplay` and remove tests for deleted modules
- **Verbose mode** (`--verbose`) shows a scrolling log panel during the run and writes the full log to a timestamped file on close

## Capabilities

### New Capabilities
- `cli-live-display`: Rich-based TUI display for `gitbench run` with per-model progress panels, live comparison summary table, human-readable token/cost formatting, and verbose log output

### Modified Capabilities
<!-- None — all existing specs cover the Astro web UI and data pipeline, which are unchanged. -->

## Impact

- **Dependencies**: Adds `rich>=13.0.0` to required dependencies
- **Code removed**: `gitbench/ui/terminal.py`, `gitbench/ui/progress.py`, `gitbench/ui/summary.py` (~200 lines)
- **Code added**: `gitbench/ui/display.py` (~300 lines), `gitbench/ui/format.py` (~30 lines)
- **Code modified**: `cli.py` (imports and initialization), `gitbench/ui/__init__.py` (exports)
- **Tests**: `tests/test_cli.py` — replace `TestTerminalProgressTable` and `TestSummaryTable` with `TestRichProgressDisplay`; remove `TestShouldUseColors`
- **Protocol unchanged**: `RunProgress` protocol in `harness/runner.py` is untouched
- **Runner unchanged**: `BenchmarkRunner` is untouched
- **No breaking changes** to CLI flags, output file formats, or the JSON/JSONL output path
