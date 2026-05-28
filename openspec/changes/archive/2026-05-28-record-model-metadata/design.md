## Context

GitBench runs benchmark fixtures by calling model APIs through adapters (`OpenAIAdapter`, `OllamaAdapter`, `MockModelClient`). Each adapter's `generate()` returns `{"text": str, "usage": dict | None}`. The runner maps these to a `Score` dataclass which flows through JSON envelopes, CSV exports, and a SQLite-backed web report.

Currently discarded during this pipeline: reasoning token counts (present in OpenAI API usage details), the actual API call latency (drowned in wall-clock measurement), and the full conversation transcript including any reasoning content the model returns.

This design adds three fields to the contract without changing the existing API surface—new fields are additive and None-able.

## Goals / Non-Goals

**Goals:**
- Record `reasoning_tokens` from model API usage details on every successful fixture run
- Record `api_duration_ms` (successful API call only, no retry overhead) alongside existing wall-clock `duration_ms`
- Record the full `transcript` (messages sent + assistant response + reasoning_content) per fixture
- Make `MockModelClient` return all three fields with realistic hardcoded data for pipeline testing
- Zero changes to export, rendering, or web layer—data flows through silently

**Non-Goals:**
- Modifying web rendering to display new fields
- Changing CSV/SQLite schema (new fields coexist via `score.get()` patterns already in use)
- Multi-attempt API timing aggregation (we only measure the successful attempt)
- Per-fixture transcript configuration (uniform: always record if available)

## Decisions

### Decision 1: Expand `ModelInterface.generate()` return dict rather than adding new methods

**Chosen**: Add `transcript`, `api_duration_ms`, and `reasoning_tokens` (in `usage`) to the existing return dict.

**Alternatives considered**:
- Separate `get_transcript()` method → adds complexity, requires two calls per fixture
- Callback/observer pattern → overengineered for 3 fields

**Rationale**: The return dict is already a loosely-typed bag. Adding keys is backward-compatible (existing code ignores unknown keys). Each adapter constructs the dict differently but the runner only reads from it.

### Decision 2: Measure API time inside each adapter, not in the runner

**Chosen**: Each adapter's `generate()` times its own successful API call and returns `api_duration_ms`.

**Alternatives considered**:
- Timing in `_run_fixture()` around the `generate()` call → can't distinguish retry overhead, doesn't work for MockModelClient sleep simulation
- Timing in a wrapper/decorator → adds indirection with marginal benefit

**Rationale**: The adapter knows best where the actual network call is. For `OpenAIAdapter`, it's `client.chat.completions.create(...)`. For `MockModelClient`, it's `time.sleep(0.01)` to simulate latency. The threading/retry pattern in `OpenAIAdapter` makes this slightly tricky—the timer goes inside the `call_api()` closure.

### Decision 3: Transcript as inline JSON list in Score, not a sidecar file

**Chosen**: `transcript: list[dict] | None` on the `Score` dataclass, serialized inline in the JSON envelope.

**Alternatives considered**:
- Sidecar `.transcript.json` files per fixture → cleaner separation but adds file management complexity, harder to query
- Gzip compression in JSON → early optimization, not needed yet

**Rationale**: The user explicitly chose inline JSON. Transcripts are 10-50KB each. The SQLite ingestion in `render.py` already reads from the JSON envelope. Inline transcripts flow naturally through the existing pipeline.

### Decision 4: Uniform hardcoded data in MockModelClient

**Chosen**: `MockModelClient` returns fixed token counts (input=50, output=30, total=80, reasoning=20), 10ms simulated API time, and builds transcript from supplied messages + mock response.

**Alternatives considered**:
- Per-fixture mock data configuration → adds complexity without benefit for testing
- Random/variable mock data → makes tests non-deterministic

**Rationale**: The mock is a development/testing tool. Uniform data is predictable and sufficient to exercise the full pipeline.

### Decision 5: Reasoning tokens extracted from OpenAI's `completion_tokens_details`

**Chosen**: Extract `reasoning_tokens` from `response.usage.completion_tokens_details.reasoning_tokens` in `OpenAIAdapter`.

**Rationale**: This is the OpenAI API's canonical location for reasoning token counts (used by o1, o3, o4-mini, etc.). Other providers may use different paths; each adapter handles its own extraction.

## Risks / Trade-offs

- **Risk**: Transcripts bloat JSON result files. A 20-fixture benchmark × 20KB transcript = 400KB extra per run. → **Mitigation**: JSON compresses well (~5:1 with gzip). Users who need compact storage can gzip result files. If it becomes a problem, we can add a `--no-transcript` CLI flag later without changing the data model.
- **Risk**: `reasoning_tokens` may be absent or differently shaped across providers. → **Mitigation**: Field is `int | None`, silently omitted from JSON when absent. Each adapter applies its own extraction logic.
- **Risk**: `api_duration_ms` is measured differently across adapters (OpenAI SDK timing vs Ollama stdlib urllib timing). → **Mitigation**: Both use `time.perf_counter()` around the HTTP call. Small differences are acceptable—this is comparative, not absolute.
- **Trade-off**: Adding fields to `Score.to_dict()`'s `none_fields` tuple means old fields also still get omitted. No behavior change for existing consumers.

## Open Questions

None—all design decisions resolved during exploration.
