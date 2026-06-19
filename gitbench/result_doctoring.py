"""Utilities for selectively repairing transient failures in result files."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DOCTORABLE_ERROR_PATTERNS = (
    "[Errno 24] Too many open files",
    "Model call timed out after",
    "RateLimitError",
    "APITimeoutError",
    "APIConnectionError",
    "InternalServerError",
)

_HTTP_STATUS_BEFORE = r"(?:api|http|provider|response|returned|server|status)"
_HTTP_STATUS_AFTER = (
    r"(?:bad gateway|error|gateway timeout|rate limit|response|server|"
    r"status|timeout|too many requests|unavailable)"
)

DOCTORABLE_HTTP_STATUS_PATTERNS = tuple(
    (
        status,
        re.compile(
            rf"\b{_HTTP_STATUS_BEFORE}\b[^\n]{{0,80}}\b{status}\b|"
            rf"\b{status}\b[^\n]{{0,80}}\b{_HTTP_STATUS_AFTER}\b",
            re.IGNORECASE,
        ),
    )
    for status in ("429", "500", "502", "503", "504")
)
RESULT_TIMESTAMP_DIR_RE = re.compile(r"^\d{8}T\d{6}Z$")
RETRY_MARKER = "_doctor_retried"


@dataclass(frozen=True)
class RerunTarget:
    """A grouped set of fixture IDs to rerun for one profile/model/benchmark."""

    profile: str
    model: str
    benchmark: str
    fixture_ids: tuple[str, ...]


@dataclass(frozen=True)
class ZeroPassModel:
    """A model that scored 0% pass across all benchmarks."""

    profile: str
    model: str
    total_fixtures: int
    total_errors: int


@dataclass(frozen=True)
class ZeroPassFixture:
    """A fixture that failed in every model that ran it."""

    fixture_id: str
    model_count: int
    benchmarks: set[str]
    errors: list[tuple[str, str | None]]  # (model_name, error_message)


@dataclass(frozen=True)
class ZeroPassModelBenchmark:
    """A (profile, model, benchmark) with 0% pass rate."""

    profile: str
    model: str
    benchmark: str
    total_fixtures: int


@dataclass
class RerunPlan:
    """Doctoring plan derived from a result payload."""

    targets: list[RerunTarget]
    pattern_counts: dict[str, int] = field(default_factory=dict)
    zero_pass_models: list[ZeroPassModel] = field(default_factory=list)
    zero_pass_fixtures: list[ZeroPassFixture] = field(default_factory=list)
    zero_pass_model_benchmarks: list[ZeroPassModelBenchmark] = field(default_factory=list)

    @property
    def doctorable_count(self) -> int:
        return sum(len(target.fixture_ids) for target in self.targets)

    @property
    def affected_models(self) -> set[tuple[str, str]]:
        return {(target.profile, target.model) for target in self.targets}

    @property
    def affected_model_benchmarks(self) -> set[tuple[str, str, str]]:
        return {
            (target.profile, target.model, target.benchmark)
            for target in self.targets
        }


def doctorable_error_pattern(error: str | None) -> str | None:
    """Return the matching doctorable pattern for an error string."""
    if not error:
        return None
    for pattern in DOCTORABLE_ERROR_PATTERNS:
        if pattern in error:
            return pattern
    for pattern, regex in DOCTORABLE_HTTP_STATUS_PATTERNS:
        if regex.search(error):
            return pattern
    return None


def is_doctorable_error(error: str | None) -> bool:
    """Whether an error string represents a transient doctorable failure."""
    return doctorable_error_pattern(error) is not None


def find_timestamped_result_files(results_root: str | Path = "gitbench-results") -> list[Path]:
    """Find JSON result files in timestamped result directories."""
    root = Path(results_root)
    if not root.exists():
        return []

    result_files: list[Path] = []
    for timestamp_dir in sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and RESULT_TIMESTAMP_DIR_RE.fullmatch(path.name)
    ):
        result_files.extend(
            path for path in timestamp_dir.glob("*.json") if path.is_file()
        )

    return sorted(result_files)

def load_result_payload(path: str | Path) -> dict[str, Any]:
    """Load a result JSON payload."""
    return json.loads(Path(path).read_text())


def write_result_payload(path: str | Path, payload: dict[str, Any]) -> Path:
    """Write a result JSON payload."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, allow_nan=False))
    return output_path


def find_zero_pass_models(payload: dict[str, Any]) -> list[ZeroPassModel]:
    """Find models with 0% pass rate across all benchmarks."""
    model_stats: dict[tuple[str, str], dict[str, int]] = {}
    for profile_name, model_entry, _result in _iter_model_results(payload):
        model_name = str(model_entry.get("model", ""))
        key = (profile_name, model_name)
        if key not in model_stats:
            summary = model_entry.get("summary", {})
            model_stats[key] = {
                "total_fixtures": summary.get("total_fixtures", 0),
                "total_passed": summary.get("total_passed", 0),
                "total_errors": 0,
            }

    # Count errors across results for each model
    for profile_name, model_entry, result in _iter_model_results(payload):
        model_name = str(model_entry.get("model", ""))
        key = (profile_name, model_name)
        if key in model_stats:
            model_stats[key]["total_errors"] += result.get("errors", 0)

    zero_pass = []
    for (profile, model), stats in model_stats.items():
        if stats["total_fixtures"] > 0 and stats["total_passed"] == 0:
            zero_pass.append(
                ZeroPassModel(
                    profile=profile,
                    model=model,
                    total_fixtures=stats["total_fixtures"],
                    total_errors=stats["total_errors"],
                )
            )
    return sorted(zero_pass, key=lambda m: (m.profile, m.model))


def find_zero_pass_fixtures(payload: dict[str, Any]) -> list[ZeroPassFixture]:
    """Find fixtures that failed in every model that ran them."""
    # Track: fixture_id -> { model_name: (passed, error, benchmark) }
    fixture_records: dict[str, dict[str, tuple[bool, str | None, str]]] = {}

    for _profile_name, model_entry, result in _iter_model_results(payload):
        model_name = str(model_entry.get("model", ""))
        benchmark_name = str(result.get("benchmark", ""))
        for score in result.get("scores", []):
            fixture_id = str(score.get("fixture_id", ""))
            if not fixture_id:
                continue
            if fixture_id not in fixture_records:
                fixture_records[fixture_id] = {}
            fixture_records[fixture_id][model_name] = (
                bool(score.get("passed")),
                score.get("error"),
                benchmark_name,
            )

    zero_pass = []
    for fixture_id, model_records in fixture_records.items():
        model_count = len(model_records)
        if model_count == 0:
            continue
        all_failed = all(not passed for passed, _err, _bench in model_records.values())
        if not all_failed:
            continue
        benchmarks = {bench for _passed, _err, bench in model_records.values()}
        errors = [
            (model, err)
            for model, (_passed, err, _bench) in model_records.items()
        ]
        zero_pass.append(
            ZeroPassFixture(
                fixture_id=fixture_id,
                model_count=model_count,
                benchmarks=benchmarks,
                errors=errors,
            )
        )
    return sorted(zero_pass, key=lambda f: f.fixture_id)


def find_zero_pass_model_benchmarks(payload: dict[str, Any]) -> list[ZeroPassModelBenchmark]:
    """Find (profile, model, benchmark) tuples with 0% pass rate.

    These are cases where a model passed some benchmarks but scored 0% in
    specific ones — indicating a possible issue with that model/benchmark pair.
    """
    results: list[ZeroPassModelBenchmark] = []
    for profile_name, model_entry, result in _iter_model_results(payload):
        model_name = str(model_entry.get("model", ""))
        benchmark_name = str(result.get("benchmark", ""))
        if not profile_name or not model_name:
            continue
        total = result.get("total", 0)
        passed = result.get("passed", 0)
        if total > 0 and passed == 0:
            results.append(
                ZeroPassModelBenchmark(
                    profile=profile_name,
                    model=model_name,
                    benchmark=benchmark_name,
                    total_fixtures=total,
                )
            )
    return sorted(results, key=lambda m: (m.profile, m.model, m.benchmark))


def build_rerun_plan(payload: dict[str, Any]) -> RerunPlan:
    """Scan a result payload for doctorable scores grouped by rerun target."""
    grouped: dict[tuple[str, str, str], set[str]] = {}
    pattern_counts: dict[str, int] = {}

    for profile_name, model_entry, result in _iter_model_results(payload):
        model_name = str(model_entry.get("model", ""))
        benchmark_name = str(result.get("benchmark", ""))
        if not profile_name or not model_name:
            continue

        result_pattern = doctorable_error_pattern(result.get("error"))
        if result_pattern:
            key = (profile_name, model_name, benchmark_name)
            fixture_ids = _fixture_ids_for_result(result)
            grouped.setdefault(key, set()).update(fixture_ids)
            pattern_counts[result_pattern] = (
                pattern_counts.get(result_pattern, 0) + len(fixture_ids)
            )

        for score in result.get("scores", []):
            pattern = doctorable_error_pattern(score.get("error"))
            if not pattern:
                continue
            key = (profile_name, model_name, benchmark_name)
            fixture_id = str(score.get("fixture_id", ""))
            if not fixture_id:
                continue
            grouped.setdefault(key, set()).add(fixture_id)
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

    targets = [
        RerunTarget(profile, model, benchmark, tuple(sorted(fixture_ids)))
        for (profile, model, benchmark), fixture_ids in sorted(grouped.items())
        if fixture_ids
    ]
    return RerunPlan(
        targets=targets,
        pattern_counts=pattern_counts,
        zero_pass_models=find_zero_pass_models(payload),
        zero_pass_fixtures=find_zero_pass_fixtures(payload),
        zero_pass_model_benchmarks=find_zero_pass_model_benchmarks(payload),
    )


def build_zero_pass_targets(payload: dict[str, Any]) -> list[RerunTarget]:
    """Build rerun targets for zero-pass models and fixtures.

    Zero-pass models get a target per (profile, model, benchmark) to rerun
    ALL fixtures in that benchmark. Zero-pass fixtures get a target per
    (profile, model, benchmark) to rerun those specific fixture IDs.

    Skips fixtures already marked with _doctor_retried=True.
    """
    zero_models = find_zero_pass_models(payload)
    zero_fixtures = find_zero_pass_fixtures(payload)
    zero_mb = find_zero_pass_model_benchmarks(payload)

    zero_model_set = {(m.profile, m.model) for m in zero_models}
    zero_fixture_set = {f.fixture_id for f in zero_fixtures}
    zero_mb_set = {(m.profile, m.model, m.benchmark) for m in zero_mb}

    # Collect already-retried fixture IDs from the payload. The marker belongs
    # to a specific model/benchmark/fixture result, not every same-named fixture.
    already_retried: set[tuple[str, str, str, str]] = set()
    for profile_name, model_entry, result in _iter_model_results(payload):
        model_name = str(model_entry.get("model", ""))
        benchmark_name = str(result.get("benchmark", ""))
        for score in result.get("scores", []):
            if score.get(RETRY_MARKER):
                fixture_id = str(score.get("fixture_id", ""))
                already_retried.add(
                    (profile_name, model_name, benchmark_name, fixture_id)
                )

    targets: list[RerunTarget] = []
    seen: set[tuple[str, str, str]] = set()

    for profile_name, model_entry, result in _iter_model_results(payload):
        model_name = str(model_entry.get("model", ""))
        benchmark_name = str(result.get("benchmark", ""))

        # Skip entries with empty profile or model names
        if not profile_name or not model_name:
            continue

        key = (profile_name, model_name, benchmark_name)
        if key in seen:
            continue

        all_fixture_ids = [
            str(score.get("fixture_id", ""))
            for score in result.get("scores", [])
        ]
        all_fixture_ids = [fid for fid in all_fixture_ids if fid]

        target_ids: list[str] = []

        # If model is zero-pass OR this is a zero-pass model-benchmark,
        # rerun all fixtures in this benchmark
        mb_key = (profile_name, model_name, benchmark_name)
        if (profile_name, model_name) in zero_model_set or mb_key in zero_mb_set:
            target_ids = [
                fid
                for fid in all_fixture_ids
                if (
                    profile_name,
                    model_name,
                    benchmark_name,
                    fid,
                ) not in already_retried
            ]
        else:
            # Add any zero-pass fixtures that appear in this benchmark
            target_ids = [
                fid for fid in all_fixture_ids
                if (
                    fid in zero_fixture_set
                    and (
                        profile_name,
                        model_name,
                        benchmark_name,
                        fid,
                    ) not in already_retried
                )
            ]

        if target_ids:
            targets.append(
                RerunTarget(
                    profile=profile_name,
                    model=model_name,
                    benchmark=benchmark_name,
                    fixture_ids=tuple(sorted(target_ids)),
                )
            )
        seen.add(key)

    return targets


def format_zero_pass_summary(plan: RerunPlan) -> str:
    """Format zero-pass model and fixture findings as a string."""
    lines: list[str] = []
    if plan.zero_pass_models:
        lines.append(f"100%-failure models ({len(plan.zero_pass_models)}):")
        for m in plan.zero_pass_models:
            lines.append(
                f"  - {m.profile}/{m.model}: "
                f"{m.total_fixtures} fixtures, {m.total_errors} errors"
            )
    if plan.zero_pass_model_benchmarks:
        if lines:
            lines.append("")
        lines.append(
            f"100%-failure model/benchmark pairs "
            f"({len(plan.zero_pass_model_benchmarks)}):"
        )
        for mb in plan.zero_pass_model_benchmarks:
            lines.append(
                f"  - {mb.profile}/{mb.model}/{mb.benchmark}: "
                f"{mb.total_fixtures} fixtures"
            )
    if plan.zero_pass_fixtures:
        if lines:
            lines.append("")
        lines.append(f"100%-failure fixtures ({len(plan.zero_pass_fixtures)}):")
        for f in plan.zero_pass_fixtures:
            bench_list = ", ".join(sorted(f.benchmarks))
            err_preview = f.errors[0][1] if f.errors else ""
            first_error = f" — {err_preview[:60]}" if err_preview else ""
            lines.append(
                f"  - {f.fixture_id}: "
                f"failed in {f.model_count} model(s) [{bench_list}]{first_error}"
            )
    return "\n".join(lines)


def format_dry_run_summary(plan: RerunPlan) -> str:
    """Format a human-readable dry-run summary (doctorable errors only)."""
    lines = [
        "Doctor dry run",
        f"Doctorable failed fixtures: {plan.doctorable_count}",
        f"Affected models: {len(plan.affected_models)}",
        f"Affected model/benchmark pairs: {len(plan.affected_model_benchmarks)}",
        "Error patterns:",
    ]
    if plan.pattern_counts:
        for pattern, count in sorted(plan.pattern_counts.items()):
            lines.append(f"  - {pattern}: {count}")
    else:
        lines.append("  - none: 0")
    return "\n".join(lines)


def mark_scores_retried(payload: dict[str, Any], target: "RerunTarget") -> None:
    """Mark the target's fixture IDs as already retried in the payload."""
    result = _find_benchmark_result(payload, target)
    target_ids = set(target.fixture_ids)
    for score in result.get("scores", []):
        if str(score.get("fixture_id", "")) in target_ids:
            score[RETRY_MARKER] = True


def replace_scores_and_recompute(
    payload: dict[str, Any],
    target: RerunTarget,
    replacement_result: dict[str, Any],
) -> None:
    """Replace target score objects from a benchmark rerun and recompute summaries."""
    replacements = {
        str(score.get("fixture_id")): score
        for score in replacement_result.get("scores", [])
    }
    expected = set(target.fixture_ids)
    missing = sorted(expected - set(replacements))
    if missing:
        raise ValueError(
            f"Rerun for {target.model}/{target.benchmark} did not return "
            f"fixture id(s): {', '.join(missing)}"
        )

    result = _find_benchmark_result(payload, target)
    if not result.get("scores"):
        result.clear()
        result.update(replacement_result)
        _recompute_benchmark_result(result)
        recompute_summaries(payload)
        return

    for index, score in enumerate(result.get("scores", [])):
        fixture_id = str(score.get("fixture_id"))
        if fixture_id in expected:
            result["scores"][index] = replacements[fixture_id]

    _recompute_benchmark_result(result)
    recompute_summaries(payload)


def recompute_summaries(payload: dict[str, Any]) -> None:
    """Recompute benchmark, model, profile, and top-level summaries in-place."""
    for _profile_name, _model_entry, result in _iter_model_results(payload):
        _recompute_benchmark_result(result)

    profiles = payload.get("profiles")
    if isinstance(profiles, list):
        for profile_entry in profiles:
            for model_entry in profile_entry.get("models", []):
                _recompute_model_summary(model_entry)
            _recompute_profile_summary(profile_entry)
        _recompute_top_summary(payload)
        return

    if isinstance(payload.get("models"), list):
        for model_entry in payload["models"]:
            _recompute_model_summary(model_entry)
        _recompute_models_top_summary(payload)
        return

    if isinstance(payload.get("results"), list):
        _recompute_model_summary(payload)
        return

    if "scores" in payload:
        _recompute_benchmark_result(payload)


def _iter_model_results(payload: dict[str, Any]):
    profiles = payload.get("profiles")
    if isinstance(profiles, list):
        for profile_entry in profiles:
            profile_name = str(profile_entry.get("profile", ""))
            for model_entry in profile_entry.get("models", []):
                for result in model_entry.get("results", []):
                    yield profile_name, model_entry, result
        return

    models = payload.get("models")
    if isinstance(models, list):
        profile_name = str(payload.get("profile", ""))
        for model_entry in models:
            for result in model_entry.get("results", []):
                yield profile_name, model_entry, result
        return

    if isinstance(payload.get("results"), list):
        model_entry = payload
        profile_name = str(payload.get("profile", ""))
        for result in payload.get("results", []):
            yield profile_name, model_entry, result
        return

    if "scores" in payload:
        yield str(payload.get("profile", "")), payload, payload


def _find_benchmark_result(payload: dict[str, Any], target: RerunTarget) -> dict[str, Any]:
    for profile_name, model_entry, result in _iter_model_results(payload):
        if (
            profile_name == target.profile
            and str(model_entry.get("model", "")) == target.model
            and str(result.get("benchmark", "")) == target.benchmark
        ):
            return result
    raise ValueError(
        f"Could not find result for profile={target.profile!r}, "
        f"model={target.model!r}, benchmark={target.benchmark!r}"
    )


def _fixture_ids_for_result(result: dict[str, Any]) -> list[str]:
    score_ids = [
        str(score.get("fixture_id", ""))
        for score in result.get("scores", [])
        if score.get("fixture_id")
    ]
    if score_ids:
        return score_ids

    benchmark_name = str(result.get("benchmark", ""))
    if not benchmark_name:
        return []

    fixture_dir = Path("fixtures") / benchmark_name
    if not fixture_dir.exists():
        return []
    return sorted(path.stem for path in fixture_dir.glob("*.yaml") if path.is_file())


def _recompute_benchmark_result(result: dict[str, Any]) -> None:
    scores = result.get("scores", [])
    total = len(scores)
    passed = sum(1 for score in scores if score.get("passed"))
    errors = sum(1 for score in scores if score.get("error"))
    result["total"] = total
    result["passed"] = passed
    result["errors"] = errors
    result["pass_at_k"] = round(passed / total, 4) if total else 0.0

    durations = [
        score.get("duration_ms")
        for score in scores
        if score.get("duration_ms") is not None
    ]
    if durations or "total_duration_ms" in result:
        result["total_duration_ms"] = round(sum(durations), 2)


def _recompute_model_summary(model_entry: dict[str, Any]) -> None:
    results = model_entry.get("results", [])
    total_fixtures = sum(result.get("total", 0) for result in results)
    total_passed = sum(result.get("passed", 0) for result in results)
    summary = model_entry.setdefault("summary", {})
    summary["total_benchmarks"] = len(results)
    summary["total_fixtures"] = total_fixtures
    summary["total_passed"] = total_passed
    summary["overall_pass_at_k"] = (
        round(total_passed / total_fixtures, 4)
        if total_fixtures
        else 0.0
    )


def _recompute_profile_summary(profile_entry: dict[str, Any]) -> None:
    models = profile_entry.get("models", [])
    total_fixtures = sum(
        model.get("summary", {}).get("total_fixtures", 0)
        for model in models
    )
    total_passed = sum(
        model.get("summary", {}).get("total_passed", 0)
        for model in models
    )
    summary = profile_entry.setdefault("summary", {})
    summary["total_models"] = len(models)
    summary["total_fixtures"] = total_fixtures
    summary["total_passed"] = total_passed
    summary["overall_pass_at_k"] = (
        round(total_passed / total_fixtures, 4)
        if total_fixtures
        else 0.0
    )


def _recompute_top_summary(payload: dict[str, Any]) -> None:
    profiles = payload.get("profiles", [])
    total_models = sum(
        profile.get("summary", {}).get("total_models", 0)
        for profile in profiles
    )
    total_fixtures = sum(
        profile.get("summary", {}).get("total_fixtures", 0)
        for profile in profiles
    )
    total_passed = sum(
        profile.get("summary", {}).get("total_passed", 0)
        for profile in profiles
    )
    summary = payload.setdefault("summary", {})
    summary["total_profiles"] = len(profiles)
    summary["total_models"] = total_models
    summary["total_fixtures"] = total_fixtures
    summary["total_passed"] = total_passed
    summary["overall_pass_at_k"] = (
        round(total_passed / total_fixtures, 4)
        if total_fixtures
        else 0.0
    )


def _recompute_models_top_summary(payload: dict[str, Any]) -> None:
    models = payload.get("models", [])
    total_fixtures = sum(
        model.get("summary", {}).get("total_fixtures", 0)
        for model in models
    )
    total_passed = sum(
        model.get("summary", {}).get("total_passed", 0)
        for model in models
    )
    summary = payload.setdefault("summary", {})
    summary["total_models"] = len(models)
    summary["total_fixtures"] = total_fixtures
    summary["total_passed"] = total_passed
    summary["overall_pass_at_k"] = (
        round(total_passed / total_fixtures, 4)
        if total_fixtures
        else 0.0
    )
