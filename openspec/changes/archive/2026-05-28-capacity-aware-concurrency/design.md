## Context

The CLI currently schedules work at two independent levels: `--model-workers` runs whole model results concurrently, and `--fixture-workers` runs fixtures concurrently inside a single model/benchmark run. The product of those values is the actual number of simultaneous model API calls, but rate limits are enforced by upstream capacity buckets such as OpenRouter upstream provider/family limits or first-party provider account limits.

GitBench also treats effort as part of the model display string. Effort is a GitBench-owned execution dimension and must not create a separate concurrency capacity bucket. A run target such as `anthropic/claude-opus-4.7:max` should display and record `max`, but its capacity identity should be derived from `anthropic/claude-opus-4.7`.

## Goals / Non-Goals

**Goals:**
- Gate every real model API call through global and capacity-group request budgets.
- Infer useful OpenRouter capacity groups from configured model strings after stripping GitBench effort.
- Ensure related OpenRouter upstream families, such as `anthropic/claude-opus-4.7` and `anthropic/claude-opus-4.8`, share one inferred group.
- Allow explicit config overrides for transports and model families where inference is unavailable or too coarse/fine.
- Preserve existing output shapes, progress display labels, and deterministic result ordering.
- Add `max` to the valid provider-agnostic GitBench effort values.

**Non-Goals:**
- Implement adaptive rate-limit tuning based on provider responses.
- Model token-per-minute or cost-per-minute limits separately from concurrent request limits.
- Remove existing CLI flags in this change.
- Guarantee perfect model-family inference for every OpenRouter provider.

## Decisions

### Use Request Budgets Instead of Model Worker Semantics

Every call to `ModelInterface.generate()` will acquire a global request permit and a capacity-group request permit. The scheduler may still use threads for model and fixture work, but model API calls cannot exceed configured budgets.

Rationale: rate limits are hit at request time. Gating only model runs does not protect against `fixture_workers > 1`, and gating only fixtures does not protect against multiple models in the same upstream bucket.

Alternative considered: group model runs and execute model/effort combinations sequentially. This reduces bursts, but it still leaks concurrency through fixture workers and underuses safe parallelism across independent capacity groups.

### Parse GitBench Effort Before Grouping

Model strings will be parsed into `base_model_id` and `effort` before capacity grouping. Effort suffixes are recognized when the final `#segment` or `:segment` is one of the valid effort values: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, or `max`.

Examples:
- `openai/gpt-5.4-mini:high` -> base `openai/gpt-5.4-mini`, effort `high`
- `anthropic/claude-opus-4.7:max` -> base `anthropic/claude-opus-4.7`, effort `max`
- `llama3.1:8b` -> base `llama3.1:8b`, effort `None`
- `llama3.1:8b:high` -> base `llama3.1:8b`, effort `high`

Rationale: colon appears in existing model IDs, so a colon suffix is effort only when it matches the known effort enum.

Alternative considered: keep only `#level`. This conflicts with current result/config conventions that already use colon effort labels in model pages and OpenRouter-style examples.

### Infer OpenRouter Capacity Groups From Base Model IDs

For profiles whose base URL points at OpenRouter, capacity grouping will use provider-aware family inference from the base model ID:

- `anthropic/claude-opus-*` -> `openrouter:anthropic/claude-opus`
- `anthropic/claude-sonnet-*` -> `openrouter:anthropic/claude-sonnet`
- `anthropic/claude-haiku-*` -> `openrouter:anthropic/claude-haiku`
- `openai/gpt-5.*` and `openai/gpt-5-*` -> `openrouter:openai/gpt-5`
- `google/gemini-3*` -> `openrouter:google/gemini-3`

When no provider-specific family rule matches, the fallback inferred group is `openrouter:<base_model_id>`.

Rationale: OpenRouter model IDs carry upstream provider and model-family information. Grouping by the GitBench profile name would serialize too much work, while grouping by exact model ID would allow related upstream variants to collide with shared limits.

Alternative considered: require all OpenRouter groups to be configured explicitly. This is accurate but too heavy for the common case because most GitBench models are currently in one OpenRouter profile.

### Keep Explicit Overrides Above Inference

Config will allow explicit concurrency groups to override inferred groups. Overrides match against the base model ID after effort stripping. A matched override provides the capacity key and optional request limit.

Representative config shape:

```json
{
  "concurrency": {
    "max_concurrent_requests": 4,
    "groups": [
      {
        "key": "openrouter:anthropic/claude-opus",
        "match": ["anthropic/claude-opus-*"],
        "max_concurrent_requests": 1
      }
    ]
  },
  "models": {
    "openrouter": {
      "base_url": "https://openrouter.ai/api/v1",
      "max_concurrent_requests": 2,
      "model": ["anthropic/claude-opus-4.7:max"]
    }
  }
}
```

Rationale: inference should cover OpenRouter’s common model naming conventions, but user configuration must be able to correct provider-specific quota topology.

Alternative considered: store concurrency metadata beside each model string. That is precise but repetitive for effort sweeps and large model lists.

### Preserve Existing Output and Ordering

Scheduling may complete work out of order, but output must be assembled in the same order that current CLI modes expose: profile order, model order, benchmark order, fixture order. Per-run JSON, JSONL, and stdout structures remain backward compatible.

Rationale: the report pipeline and tests depend on stable model/fixture ordering.

## Risks / Trade-offs

- [Risk] OpenRouter inference groups unrelated models too broadly or too narrowly. -> Mitigation: keep inference conservative, document rules, and let explicit config overrides win.
- [Risk] Request-budget gating reduces throughput for users with higher quotas. -> Mitigation: expose global, profile, and group request limits so users can raise budgets intentionally.
- [Risk] Supporting both `#effort` and `:effort` creates parsing ambiguity. -> Mitigation: only parse a suffix as effort when the final segment exactly matches the GitBench effort enum.
- [Risk] Threaded progress updates may arrive in a different order. -> Mitigation: keep progress event labels stable and preserve output ordering separately from completion ordering.
- [Risk] Existing tests assume `--model-workers` directly maps to concurrently running models. -> Mitigation: update tests to assert request-budget behavior and retain compatibility tests for independent capacity groups.

## Migration Plan

1. Add shared effort parsing that supports `#effort` and `:effort`, including `max`.
2. Add capacity-group derivation with OpenRouter inference and explicit override support.
3. Introduce request-budget coordination around model API calls.
4. Wire CLI/profile config into the scheduler while preserving existing flags and defaults.
5. Update docs and tests.

Rollback is straightforward because the change is internal scheduling/config parsing. Existing output files remain compatible.
