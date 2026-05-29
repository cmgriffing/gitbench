## 1. Effort Parsing

- [x] 1.1 Consolidate model effort parsing so `#effort` and `:effort` suffixes are handled by one shared parser.
- [x] 1.2 Add `max` to the valid GitBench effort values and update validation for Anthropic/OpenRouter examples.
- [x] 1.3 Update OpenAI, Ollama, and mock adapter construction to use the shared parser and preserve full model labels for output.
- [x] 1.4 Add tests for colon effort parsing, Ollama-style colon tags, and `anthropic/claude-opus-4.7:max`.

## 2. Capacity Group Derivation

- [x] 2.1 Add a capacity-group derivation module or helper that accepts profile config plus full model string and returns base model ID, effort, capacity key, and request limit.
- [x] 2.2 Implement OpenRouter inference rules for Anthropic Opus/Sonnet/Haiku, OpenAI GPT-5 families, Google Gemini 3 families, and fallback exact-base-model grouping.
- [x] 2.3 Implement explicit concurrency group override matching against base model IDs after effort stripping.
- [x] 2.4 Add tests proving `anthropic/claude-opus-4.7:max` and `anthropic/claude-opus-4.8:max` share `openrouter:anthropic/claude-opus`.

## 3. Request Budget Scheduler

- [x] 3.1 Add a shared request-budget coordinator with global and per-capacity-group semaphores.
- [x] 3.2 Gate real model API calls through the coordinator immediately around `ModelInterface.generate()`.
- [x] 3.3 Ensure permits are released on success, provider error, timeout, scoring failure, and fixture cleanup paths.
- [x] 3.4 Preserve deterministic model, benchmark, and fixture output ordering while allowing out-of-order completion.

## 4. CLI And Config Wiring

- [x] 4.1 Parse global concurrency config and profile-level `max_concurrent_requests` settings.
- [x] 4.2 Wire capacity metadata into model clients or runner execution without changing existing output schemas.
- [x] 4.3 Keep `--model-workers` and `--fixture-workers` accepted while ensuring request budgets are authoritative.
- [x] 4.4 Add user-facing logging that reports effective global/profile/group request limits at run start.

## 5. Verification And Docs

- [x] 5.1 Update CLI scheduling tests to assert request-budget limits instead of raw model-worker overlap for shared groups.
- [x] 5.2 Update parallel fixture tests to cover group-budget gating with `fixture_workers > 1`.
- [x] 5.3 Update README/config examples for effort suffixes, `max`, OpenRouter inference, and explicit concurrency groups.
- [x] 5.4 Run targeted Python tests for reasoning, model adapters, CLI scheduling, and parallel fixtures.
