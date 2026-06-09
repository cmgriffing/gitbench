## Context

The regular `gitbench run` command uses `RequestBudgetCoordinator` with `RateLimitedBoundedSemaphore` instances to enforce per-group inter-request delays and global concurrency limits. The `gitbench doctor` command was intended to benefit from this (per the `add-rate-limiting-controls` design's Decision 1), but was never wired up — doctor creates `BenchmarkRunner` instances without a `request_budget` or `capacity_key`, so fixtures call `model_client.generate()` with no pacing.

Doctor runs targets sequentially (`fixture_workers=1`, one target at a time), so intra-group bursts aren't the concern. The risk is **cross-group bursts**: when doctoring many models from different capacity groups, finishing one target and immediately starting the next fires requests at group boundaries with zero delay. A session with 20+ targets across 10+ groups could trigger OpenRouter's global rate limit.

Adding the full `RequestBudgetCoordinator` to doctor would be over-engineered for a sequential workload — the global semaphore is a no-op with one concurrent request, and per-group intervals only help when consecutive targets happen to share a capacity group.

## Goals / Non-Goals

**Goals:**
- Add a 1-second fixed delay between doctor rerun requests to prevent upstream rate limiting
- Keep the change minimal and doctor-specific (no impact on the regular runner)
- No config surface, no CLI flags

**Non-Goals:**
- Wiring the full `RequestBudgetCoordinator` into the doctor path
- Configurable doctor-specific delay duration
- Per-group delay differentiation for doctor
- Extending the runner or capacity modules

## Decisions

### Decision 1: Sleep in `_doctor_one_file`, not in the runner

**Chosen**: A `time.sleep(1.0)` in the doctor's target loop after each `runner.run_benchmark()` call.

**Rationale**: The runner is shared between the regular `run` command (which already has proper rate limiting via `RequestBudgetCoordinator`) and `doctor`. Putting the delay in the runner would affect both paths or require conditional logic. Keeping it in `_doctor_one_file` is doctor-specific and trivial to verify.

**Alternatives considered**:
- Adding `min_request_interval_s` param to `BenchmarkRunner` → touches shared code unnecessarily
- Wiring `RequestBudgetCoordinator` into doctor → over-engineered for sequential execution; global semaphore is a no-op, per-group intervals don't cover cross-group boundaries

### Decision 2: 1-second fixed delay, not configurable

**Chosen**: Hardcoded `time.sleep(1.0)` between targets.

**Rationale**: Doctor is a recovery tool, not a performance path. A 1-second delay adds negligible overhead (1 second × N targets) while providing a safe buffer against upstream rate limits. Adding a config option (`--doctor-delay-ms`) would be YAGNI — users who need more control should adjust their upstream rate limits rather than doctor pacing.

### Decision 3: Delay between targets, not between fixtures

**Chosen**: Sleep after `runner.run_benchmark()` completes (i.e., after all fixtures in a target).

**Rationale**: With `fixture_workers=1`, fixtures within a target already run sequentially. A per-fixture sleep would compound (N fixtures × 1s = N seconds for a single target) when the real burst risk is at group boundaries. Per-target sleep is sufficient.

## Risks / Trade-offs

- **Risk**: 1 second may not be enough for providers with very strict rate limits → **Mitigation**: Doctor is a recovery tool; if a request gets 429'd, the existing retry logic (exponential backoff + Retry-After header from `add-rate-limiting-controls`) handles it. The 1s delay reduces the probability, not eliminates it.
- **Risk**: 1 second per target adds noticeable latency for many-small-target sessions → **Mitigation**: Even with 50 single-fixture targets, that's only 50 seconds added — negligible compared to model inference latency.
- **Trade-off**: Not configurable means power users can't tune it → Acceptable trade-off; doctor is an infrequent recovery tool.
