## 1. Implementation

- [x] 1.1 Add `import time` to `gitbench/cli.py` (if not already present)
- [x] 1.2 Add `time.sleep(1.0)` in `_doctor_one_file` after each target's `runner.run_benchmark()` and before advancing progress

## 2. Verification

- [x] 2.1 Run `gitbench doctor --latest --dry-run` to confirm no regressions in plan detection
- [x] 2.2 Run `gitbench doctor <result-file>` on a small result file and verify the 1-second gaps between target reruns in output timing
