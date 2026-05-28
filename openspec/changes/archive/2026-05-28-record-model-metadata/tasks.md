## 1. Score dataclass — new fields

- [x] 1.1 Add `reasoning_tokens: int | None = None`, `api_duration_ms: float | None = None`, `transcript: list[dict] | None = None` fields to `Score` dataclass in `gitbench/harness/types.py`
- [x] 1.2 Add `"reasoning_tokens"`, `"api_duration_ms"`, `"transcript"` to the `none_fields` tuple in `Score.to_dict()` so they are omitted from JSON when `None`
- [x] 1.3 Verify `Score.from_dict()` handles all three new fields (uses `**kwargs`, should work automatically)

## 2. MockModelClient — enriched test data

- [x] 2.1 In `MockModelClient.generate()`, build a transcript list from the input messages + a `{"role": "assistant", "content": self.response}` entry
- [x] 2.2 Simulate API latency with `time.sleep(0.01)` timed via `time.perf_counter()`, store as `api_duration_ms`
- [x] 2.3 Return hardcoded usage dict including `reasoning_tokens: 20` alongside existing `input_tokens`, `output_tokens`, `total_tokens`, `cost`
- [x] 2.4 Return `transcript` and `api_duration_ms` in the response dict
- [x] 2.5 Verify `set_response()` still works — doesn't need changes since it only updates `self.response` text

## 3. OpenAIAdapter — reasoning tokens, API timing, transcript

- [x] 3.1 In the `call_api()` closure, wrap `self.client.chat.completions.create()` with `time.perf_counter()` before and after to capture `api_duration_ms`
- [x] 3.2 Extract `reasoning_tokens` from `response.usage.completion_tokens_details.reasoning_tokens` (handle `None` gracefully)
- [x] 3.3 Build transcript list from input messages + assistant response entry (with `reasoning_content` key when present on the message)
- [x] 3.4 Include `reasoning_tokens` in the usage dict, `api_duration_ms` and `transcript` in the result dict

## 4. OllamaAdapter — API timing, transcript

- [x] 4.1 In the `call_api()` closure, wrap the `urllib.request.urlopen()` call with `time.perf_counter()` before and after to capture `api_duration_ms`
- [x] 4.2 Build transcript list from input messages + assistant response entry (no reasoning_content for Ollama)
- [x] 4.3 Include `api_duration_ms` and `transcript` in the result dict

## 5. Runner — wire new fields to Score

- [x] 5.1 In `_run_fixture()`, extract `transcript` from response dict and assign to `score.transcript`
- [x] 5.2 Extract `api_duration_ms` from response dict and assign to `score.api_duration_ms`
- [x] 5.3 In the usage mapping block, extract `reasoning_tokens` from usage dict and assign to `score.reasoning_tokens`

## 6. Verify with mock provider

- [x] 6.1 Run a single benchmark with mock provider to a temp output directory and confirm all three new fields appear in the JSON result file
- [x] 6.2 Confirm existing fields (`duration_ms`, token counts, pass/fail) are unaffected
- [x] 6.3 Confirm old result files without the new fields still load correctly via `Score.from_dict()`
