## Why

The `gitbench doctor` command reruns transient failures sequentially, but fires requests back-to-back with no pacing between targets. When doctoring many models across different capacity groups, rapid-fire requests at group boundaries can trigger upstream global rate limits (429), defeating the purpose of the repair.

## What Changes

- Add a 1-second fixed delay between doctor rerun targets in `_doctor_one_file`, ensuring upstream APIs are not overwhelmed even when many model groups are doctored in a single session

## Capabilities

### New Capabilities

None — this is an implementation change with no new configurable behavior.

### Modified Capabilities

None — no existing spec-level requirements are changing.

## Impact

- `gitbench/cli.py` — `_doctor_one_file` gains a `time.sleep(1.0)` between targets
- No config changes, no new CLI flags, no breaking changes
