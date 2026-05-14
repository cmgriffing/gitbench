## Context

GitBench currently has a hand-rolled terminal progress system using raw ANSI escape codes (`\x1b[1A\x1b[2K`). It renders a plain-text table to stderr during benchmark execution, then separately prints a static colored summary table to stdout after the run completes. The code is spread across three modules (`terminal.py`, `progress.py`, `summary.py`) and is fragile — hardcoded column widths, no visual hierarchy, no live comparison across models.

Rich is the de facto standard Python library for beautiful terminal output (50k+ GitHub stars, 50M+ downloads/month). It handles terminal detection, colors, layouts, progress bars, and alternate screen buffers. Using it eliminates ~200 lines of bespoke terminal code.

The `RunProgress` protocol in `harness/runner.py` is the clean integration seam — `BenchmarkRunner` calls into it via callbacks (`model_started`, `benchmark_started`, `fixture_finished`, `benchmark_finished`, `model_finished`). The runner does not need to change at all.

## Goals / Non-Goals

**Goals:**
- Rich-based live display using the alternate screen buffer (`screen=True`) for clean separation from normal terminal output
- Per-model progress panels with progress bars, live pass rates, token/cost accumulators
- Live comparison summary table that fills in as benchmarks complete across models
- Human-readable token/cost formatting (K, M, B suffixes)
- Verbose mode: scrolling log panel during run + full log dump to timestamped file on close
- Non-TTY fallback (piped/redirected stderr) that still shows progress textually
- Delete all hand-rolled terminal code; Rich becomes a required dependency
- Keep `RunProgress` protocol unchanged; add a second optional method `token_update` for accumulated token/cost data

**Non-Goals:**
- Full Textual TUI (keyboard navigation, interactive widgets) — overkill for a benchmark runner
- Changing the JSON/JSONL output format or export pipeline
- Modifying `BenchmarkRunner` or any benchmark implementations
- Live display during `gitbench report` (that's an Astro web UI concern)

## Decisions

### 1. Rich `Live` with `screen=True` (alternate screen buffer)

**Choice**: Use Rich's `Live` context manager with `screen=True`, `auto_refresh=False`.

**Rationale**: The alternate screen buffer gives a clean, self-contained display. When the run finishes and `Live.stop()` is called, the terminal returns to its previous state — no ANSI artifacts in scrollback. We then print the final static summary to stdout for permanent visibility.

**Alternatives considered**:
- `screen=False` (in-place): Leaves the last frame in scrollback, but the intermediate refresh frames are also in scrollback — messy.
- Manual `Console` with `clear()`: More fragile, no Rich render loop optimization.

### 2. Layout structure: Header → Model Panels → Summary → Log

```
Layout (root, vertical split)
├── Layout (header, size=3)         — title + elapsed
├── Layout (model_row)              — horizontal split of per-model panels
│   ├── Panel (model_1)
│   └── Panel (model_2)
├── Layout (summary_body)           — live comparison table
│   └── Table (comparison_matrix)
└── Layout (log, size=6)            — verbose log panel (conditional)
```

**Rationale**: Per-model panels side-by-side make multi-model comparison immediate. The comparison table below provides the benchmark-by-benchmark matrix. The log panel at the bottom only appears in verbose mode.

### 3. State management: Dictionaries, no dataclasses

**Choice**: Track display state in plain `dict` structures keyed by model and benchmark name.

**Rationale**: The state is transient (only exists during the run) and is purely for rendering. Dataclasses add ceremony with no benefit here — we're not serializing, validating, or passing state between modules.

**State shape**:
```python
_model_state: dict[str, dict]  # model -> {status, benches_done, benches_total,
                               #            fixtures_done, fixtures_total, passed, errors,
                               #            current_benchmark, input_tokens, output_tokens,
                               #            cost_usd}
_bench_results: dict[str, dict]  # model -> {bench -> {total, passed, errors, done}}
```

### 4. Protocol extension: `token_update` callback

**Choice**: Add an optional `token_update(self, model, input_tokens, output_tokens, cost_usd)` method to `RichProgressDisplay` (called from `fixture_finished` or a new protocol method).

**Rationale**: The existing `fixture_finished` callback doesn't carry token/cost data. Rather than changing the `RunProgress` protocol (which would force all implementors to change), we can accumulate token data within `RichProgressDisplay` itself. However, access to token data requires the runner to expose it. The simplest approach: the `RichProgressDisplay` accepts a callback registry; the runner calls `fixture_finished` as today, and we derive what we can. For token/cost, we'll extend the protocol to add `fixture_tokens(self, model, input_tokens, output_tokens, cost_usd)` as a new optional callback, or we'll pass token data through `fixture_finished` by expanding its signature.

**Actually**: Let's keep it simpler. We add two new optional methods to `RunProgress`:

```python
def fixture_token_update(self, model: str, input_tokens: int, output_tokens: int, cost_usd: float | None) -> None: ...
def token_update(self, model: str, input_tokens: int, output_tokens: int, cost_usd: float | None) -> None: ...
```

The `BenchmarkRunner` calls these after each fixture when token data is available from the model response. Non-Rich progress implementations just no-op them.

### 5. Human-readable formatting

**Choice**: A standalone `format.py` module with pure functions.

```python
def human_readable(n: int, unit: str = "") -> str:
    """1234 -> '1.2K', 1234567 -> '1.2M', 1234567890 -> '1.2B'"""
    ...

def human_readable_cost(n: float) -> str:
    """0.042 -> '$0.04', 1.234 -> '$1.23', 123.45 -> '$123.45'"""
    ...

def format_duration(seconds: float) -> str:
    """90 -> '1m30s', 45 -> '45s'"""
    ...
```

**Rationale**: Pure functions, easy to test, no Rich dependency needed for the formatting logic itself. Reused by the display class.

### 6. Verbose log: ring buffer + file dump

**Choice**: Maintain a `collections.deque` (maxlen=500) of log lines. Show last ~6 in the live panel. On `close()`, write the full buffer to `gitbench-logs/verbose-{timestamp}.log`.

**Rationale**: Real-time feedback via the panel, permanent record via the file. The file path is printed after close so the user knows where to find it.

### 7. Color thresholds match existing conventions

| Pass Rate | Color  |
|-----------|--------|
| ≥ 80%     | green  |
| 50-79%    | yellow |
| < 50%     | red    |

Delta (model 2 vs model 1): green for positive, red for negative, dim for zero.

## Risks / Trade-offs

- **[Risk] Rich adds ~2MB to install size** → Mitigation: Rich is already a transitive dependency of many Python tools; most users have it cached. It's pure Python with no C extensions.
- **[Risk] Alternate screen buffer may confuse some terminal emulators** → Mitigation: Rich handles terminal detection. If the terminal doesn't support alternate screen, Rich falls back gracefully.
- **[Risk] Verbose log file could grow large on long runs** → Mitigation: Ring buffer caps at 500 lines in memory; file is bounded by the number of fixtures × models (typically <10K lines).
- **[Trade-off] Adding optional methods to `RunProgress` protocol slightly couples the protocol to Rich-specific needs** → Acceptable: The methods are optional (no-op by default) and provide genuinely useful data (token tracking) that any future progress display would benefit from.

## Open Questions

None — all design decisions are resolved.
