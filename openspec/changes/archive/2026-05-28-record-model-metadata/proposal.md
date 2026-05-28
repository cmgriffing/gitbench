## Why

The benchmark runner captures only basic token counts and wall-clock time, discarding rich data the model APIs already return: reasoning tokens, API-level latency, and the full conversation transcript. Recording this data enables deeper analysis of model behavior—how much "thinking" each model does, how fast the provider actually responds, and what the model's raw reasoning looks like. Recording it now (without changing the web layer) ensures every future benchmark run captures this data from the start.

## What Changes

- **Reasoning token measurement**: `ModelInterface.generate()` and all adapters extract `reasoning_tokens` from API usage details. The `Score` dataclass gains a `reasoning_tokens` field. Flows through the existing JSON envelope and SQLite pipeline automatically.
- **API time measurement**: Each adapter measures the successful `generate()` call's duration independently from wall-clock time. The `Score` dataclass gains an `api_duration_ms` field. Complements (does not replace) the existing `duration_ms` wall-clock metric.
- **Full transcript recording**: `ModelInterface.generate()` now returns the complete conversation—messages sent, the assistant's response text, and any `reasoning_content` returned by the API. The `Score` dataclass gains a `transcript` field storing this as inline JSON.
- **Mock provider enrichment**: `MockModelClient` returns realistic hardcoded data for all new fields so the pipeline is testable without hitting real APIs.

## Capabilities

### New Capabilities
- `reasoning-token-measurement`: Extract and record `reasoning_tokens` from model API usage details, flowing through Score → JSON envelope → SQLite.
- `api-time-measurement`: Measure and record API call latency within each adapter, separate from wall-clock fixture duration.
- `transcript-recording`: Capture the full conversation transcript (messages sent, assistant response, reasoning content) per fixture run.

### Modified Capabilities
- `runtime-tracking`: Add `api_duration_ms` alongside the existing `duration_ms`—two complementary timing metrics with different scopes.

## Impact

- `gitbench/harness/model.py` — all three adapters (`OpenAIAdapter`, `OllamaAdapter`, `MockModelClient`) return expanded generate() dicts
- `gitbench/harness/types.py` — `Score` dataclass gains three new optional fields
- `gitbench/harness/runner.py` — `_run_fixture()` maps new response fields to Score
- `gitbench/export.py` — no changes (CSV exporters use `score.get()`, new fields silently coexist)
- `gitbench/render.py` — no changes (aggregation uses `score.get()`, web layer unchanged)
- Result JSON files grow proportionally to transcript size (10-50KB per fixture)
