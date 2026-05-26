"""Tests for result doctoring utilities."""

from gitbench.result_doctoring import (
    build_rerun_plan,
    build_zero_pass_targets,
    find_timestamped_result_files,
    find_zero_pass_fixtures,
    find_zero_pass_models,
    format_dry_run_summary,
    format_zero_pass_summary,
    is_doctorable_error,
    replace_scores_and_recompute,
)


def _combined_payload():
    return {
        "benchmark_suite_version": "0.1.0",
        "summary": {
            "total_profiles": 1,
            "total_models": 1,
            "total_fixtures": 3,
            "total_passed": 1,
            "overall_pass_at_k": 0.3333,
        },
        "profiles": [
            {
                "profile": "local",
                "summary": {
                    "total_models": 1,
                    "total_fixtures": 3,
                    "total_passed": 1,
                    "overall_pass_at_k": 0.3333,
                },
                "models": [
                    {
                        "model": "mock",
                        "summary": {
                            "total_benchmarks": 1,
                            "total_fixtures": 3,
                            "total_passed": 1,
                            "overall_pass_at_k": 0.3333,
                        },
                        "results": [
                            {
                                "benchmark": "commit_messages",
                                "total": 3,
                                "passed": 1,
                                "pass_at_k": 0.3333,
                                "errors": 2,
                                "total_duration_ms": 30,
                                "scores": [
                                    {
                                        "fixture_id": "f001",
                                        "passed": True,
                                        "similarity": 1.0,
                                        "model_output": "ok",
                                        "error": None,
                                        "duration_ms": 10,
                                    },
                                    {
                                        "fixture_id": "f002",
                                        "passed": False,
                                        "similarity": 0.0,
                                        "model_output": "",
                                        "error": "Model call timed out after 30s",
                                        "duration_ms": 10,
                                    },
                                    {
                                        "fixture_id": "f003",
                                        "passed": False,
                                        "similarity": 0.0,
                                        "model_output": "bad",
                                        "error": "expected got mismatch",
                                        "duration_ms": 10,
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    }


def test_doctorable_and_non_doctorable_errors():
    doctorable = [
        "[Errno 24] Too many open files",
        "Model call timed out after 30s",
        "RateLimitError: slow down",
        "APITimeoutError",
        "APIConnectionError",
        "InternalServerError",
        "provider returned 429",
        "provider returned HTTP 429",
        "500 server error",
        "HTTP 500 server error",
        "502 bad gateway",
        "503 unavailable",
        "504 gateway timeout",
    ]
    for error in doctorable:
        assert is_doctorable_error(error)

    assert not is_doctorable_error("expected 'foo' got 'bar'")
    assert not is_doctorable_error("expected score 500 but got 400")
    assert not is_doctorable_error("validated fixture_500 incorrectly")
    assert not is_doctorable_error("extra selected commit messages")
    assert not is_doctorable_error("command-equivalence failure")
    assert not is_doctorable_error(None)


def test_rerun_plan_groups_by_profile_model_benchmark_and_summarizes():
    payload = _combined_payload()
    payload["profiles"][0]["models"][0]["results"][0]["scores"].append(
        {
            "fixture_id": "f004",
            "passed": False,
            "similarity": 0.0,
            "model_output": "",
            "error": "[Errno 24] Too many open files",
        }
    )

    plan = build_rerun_plan(payload)

    assert plan.doctorable_count == 2
    assert len(plan.targets) == 1
    assert plan.targets[0].profile == "local"
    assert plan.targets[0].model == "mock"
    assert plan.targets[0].benchmark == "commit_messages"
    assert plan.targets[0].fixture_ids == ("f002", "f004")

    summary = format_dry_run_summary(plan)
    assert "Doctorable failed fixtures: 2" in summary
    assert "Affected models: 1" in summary
    assert "Affected model/benchmark pairs: 1" in summary
    assert "Too many open files: 1" in summary


def test_replace_scores_preserves_non_targets_and_recomputes_summaries():
    payload = _combined_payload()
    plan = build_rerun_plan(payload)
    original_f001 = dict(
        payload["profiles"][0]["models"][0]["results"][0]["scores"][0]
    )
    original_f003 = dict(
        payload["profiles"][0]["models"][0]["results"][0]["scores"][2]
    )

    replace_scores_and_recompute(
        payload,
        plan.targets[0],
        {
            "benchmark": "commit_messages",
            "total": 1,
            "passed": 1,
            "pass_at_k": 1.0,
            "errors": 0,
            "scores": [
                {
                    "fixture_id": "f002",
                    "passed": True,
                    "similarity": 1.0,
                    "model_output": "fixed",
                    "error": None,
                    "duration_ms": 5,
                }
            ],
        },
    )

    result = payload["profiles"][0]["models"][0]["results"][0]
    assert result["scores"][0] == original_f001
    assert result["scores"][2] == original_f003
    assert result["scores"][1]["model_output"] == "fixed"
    assert result["passed"] == 2
    assert result["errors"] == 1
    assert result["pass_at_k"] == 0.6667
    assert result["total_duration_ms"] == 25
    assert payload["summary"]["total_passed"] == 2
    assert payload["summary"]["overall_pass_at_k"] == 0.6667


def test_find_timestamped_result_files_returns_all_timestamped_results(tmp_path):
    ignored = tmp_path / "gitbench-results/a/results-v0.1.0.json"
    ignored_z = tmp_path / "gitbench-results/scratchZ/results-v0.1.0.json"
    older = tmp_path / "gitbench-results/20260101T000000Z/results-v0.1.0.json"
    latest = tmp_path / "gitbench-results/20260102T000000Z/results-v0.1.0.json"
    ignored.parent.mkdir(parents=True)
    ignored_z.parent.mkdir(parents=True)
    older.parent.mkdir(parents=True)
    latest.parent.mkdir(parents=True)
    ignored.write_text("{}")
    ignored_z.write_text("{}")
    older.write_text("{}")
    latest.write_text("{}")

    assert find_timestamped_result_files(tmp_path / "gitbench-results") == [
        older,
        latest,
    ]


class TestFindZeroPassModels:
    def test_no_zero_pass_models_with_mixed_results(self):
        payload = _combined_payload()
        models = find_zero_pass_models(payload)
        assert models == []

    def test_finds_models_with_zero_total_passed(self):
        payload = _combined_payload()
        # Make all fixtures fail
        for score in payload["profiles"][0]["models"][0]["results"][0]["scores"]:
            score["passed"] = False
        payload["profiles"][0]["models"][0]["results"][0]["passed"] = 0
        payload["profiles"][0]["models"][0]["results"][0]["pass_at_k"] = 0.0
        payload["profiles"][0]["models"][0]["results"][0]["errors"] = 3
        payload["profiles"][0]["models"][0]["summary"]["total_passed"] = 0
        payload["profiles"][0]["models"][0]["summary"]["overall_pass_at_k"] = 0.0
        payload["profiles"][0]["summary"]["total_passed"] = 0
        payload["profiles"][0]["summary"]["overall_pass_at_k"] = 0.0
        payload["summary"]["total_passed"] = 0
        payload["summary"]["overall_pass_at_k"] = 0.0

        models = find_zero_pass_models(payload)
        assert len(models) == 1
        assert models[0].profile == "local"
        assert models[0].model == "mock"
        assert models[0].total_fixtures == 3
        assert models[0].total_errors == 3

    def test_multiple_models_with_one_zero_pass(self):
        payload = {
            "benchmark_suite_version": "0.1.0",
            "profiles": [
                {
                    "profile": "local",
                    "models": [
                        {
                            "model": "good-model",
                            "summary": {"total_fixtures": 2, "total_passed": 1, "overall_pass_at_k": 0.5},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "total": 2,
                                    "passed": 1,
                                    "errors": 1,
                                    "scores": [
                                        {"fixture_id": "f1", "passed": True, "error": None},
                                        {"fixture_id": "f2", "passed": False, "error": "bad"},
                                    ],
                                }
                            ],
                        },
                        {
                            "model": "bad-model",
                            "summary": {"total_fixtures": 2, "total_passed": 0, "overall_pass_at_k": 0.0},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "total": 2,
                                    "passed": 0,
                                    "errors": 2,
                                    "scores": [
                                        {"fixture_id": "f1", "passed": False, "error": "timeout"},
                                        {"fixture_id": "f2", "passed": False, "error": "timeout"},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        models = find_zero_pass_models(payload)
        assert len(models) == 1
        assert models[0].profile == "local"
        assert models[0].model == "bad-model"
        assert models[0].total_fixtures == 2
        assert models[0].total_errors == 2

    def test_empty_model_skipped(self):
        payload = {
            "profiles": [
                {
                    "profile": "p",
                    "models": [
                        {
                            "model": "empty",
                            "summary": {"total_fixtures": 0, "total_passed": 0},
                            "results": [],
                        }
                    ],
                }
            ],
        }
        assert find_zero_pass_models(payload) == []


class TestFindZeroPassFixtures:
    def test_no_zero_pass_fixtures_with_mixed_results(self):
        # Need multiple models — a fixture must fail in ALL models to be zero-pass
        payload = {
            "profiles": [
                {
                    "profile": "p",
                    "models": [
                        {
                            "model": "m1",
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {"fixture_id": "fx", "passed": False, "error": "fail"},
                                        {"fixture_id": "fy", "passed": True, "error": None},
                                    ],
                                }
                            ],
                        },
                        {
                            "model": "m2",
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {"fixture_id": "fx", "passed": True, "error": None},
                                        {"fixture_id": "fy", "passed": False, "error": "fail"},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        # No fixture fails in ALL models, so zero-pass fixtures list is empty
        fixtures = find_zero_pass_fixtures(payload)
        assert fixtures == []

    def test_finds_fixture_that_fails_in_all_models(self):
        payload = {
            "benchmark_suite_version": "0.1.0",
            "profiles": [
                {
                    "profile": "local",
                    "models": [
                        {
                            "model": "model-a",
                            "summary": {},
                            "results": [
                                {
                                    "benchmark": "commit_messages",
                                    "total": 2,
                                    "passed": 1,
                                    "errors": 1,
                                    "scores": [
                                        {"fixture_id": "f1", "passed": True, "error": None},
                                        {"fixture_id": "f2", "passed": False, "error": "broken"},
                                    ],
                                }
                            ],
                        },
                        {
                            "model": "model-b",
                            "summary": {},
                            "results": [
                                {
                                    "benchmark": "commit_messages",
                                    "total": 2,
                                    "passed": 1,
                                    "errors": 1,
                                    "scores": [
                                        {"fixture_id": "f1", "passed": True, "error": None},
                                        {"fixture_id": "f2", "passed": False, "error": "also broken"},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        fixtures = find_zero_pass_fixtures(payload)
        assert len(fixtures) == 1
        assert fixtures[0].fixture_id == "f2"
        assert fixtures[0].model_count == 2
        assert fixtures[0].benchmarks == {"commit_messages"}
        assert len(fixtures[0].errors) == 2

    def test_fixture_that_passes_in_one_model_not_included(self):
        payload = {
            "profiles": [
                {
                    "profile": "p",
                    "models": [
                        {
                            "model": "m1",
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {"fixture_id": "fx", "passed": False, "error": "fail"},
                                    ],
                                }
                            ],
                        },
                        {
                            "model": "m2",
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {"fixture_id": "fx", "passed": True, "error": None},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        assert find_zero_pass_fixtures(payload) == []

    def test_fixture_only_run_by_one_model_counted(self):
        payload = {
            "profiles": [
                {
                    "profile": "p",
                    "models": [
                        {
                            "model": "only-model",
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {"fixture_id": "fx", "passed": False, "error": "dead"},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        fixtures = find_zero_pass_fixtures(payload)
        assert len(fixtures) == 1
        assert fixtures[0].fixture_id == "fx"
        assert fixtures[0].model_count == 1

    def test_skips_empty_fixture_ids(self):
        payload = {
            "profiles": [
                {
                    "profile": "p",
                    "models": [
                        {
                            "model": "m",
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {"fixture_id": "", "passed": False, "error": "x"},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        assert find_zero_pass_fixtures(payload) == []


class TestFormatZeroPassSummary:
    def test_empty_when_none_found(self):
        # Two models, each passes one fixture the other fails — no zero-pass
        payload = {
            "profiles": [
                {
                    "profile": "p",
                    "models": [
                        {
                            "model": "m1",
                            "summary": {"total_fixtures": 2, "total_passed": 1},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {"fixture_id": "fx", "passed": True, "error": None},
                                        {"fixture_id": "fy", "passed": False, "error": "fail"},
                                    ],
                                }
                            ],
                        },
                        {
                            "model": "m2",
                            "summary": {"total_fixtures": 2, "total_passed": 1},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {"fixture_id": "fx", "passed": False, "error": "fail"},
                                        {"fixture_id": "fy", "passed": True, "error": None},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        plan = build_rerun_plan(payload)
        assert format_zero_pass_summary(plan) == ""

    def test_includes_models_and_fixtures(self):
        payload = {
            "profiles": [
                {
                    "profile": "p",
                    "models": [
                        {
                            "model": "dead-model",
                            "summary": {"total_fixtures": 3, "total_passed": 0, "overall_pass_at_k": 0.0},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "total": 3,
                                    "passed": 0,
                                    "errors": 3,
                                    "scores": [
                                        {"fixture_id": "fx", "passed": False, "error": "boom"},
                                        {"fixture_id": "fy", "passed": False, "error": "dead"},
                                        {"fixture_id": "fz", "passed": False, "error": "rip"},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        plan = build_rerun_plan(payload)
        summary = format_zero_pass_summary(plan)
        assert "100%-failure models (1):" in summary
        assert "p/dead-model: 3 fixtures, 3 errors" in summary
        assert "100%-failure fixtures (3):" in summary
        assert "fx" in summary
        assert "fy" in summary
        assert "fz" in summary

    def test_dry_run_summary_focuses_on_doctorable_errors(self):
        payload = {
            "profiles": [
                {
                    "profile": "p",
                    "models": [
                        {
                            "model": "dead-model",
                            "summary": {"total_fixtures": 2, "total_passed": 0, "overall_pass_at_k": 0.0},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "total": 2,
                                    "passed": 0,
                                    "errors": 2,
                                    "scores": [
                                        {"fixture_id": "fx", "passed": False, "error": "boom"},
                                        {"fixture_id": "fy", "passed": False, "error": "dead"},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        plan = build_rerun_plan(payload)
        summary = format_dry_run_summary(plan)
        assert "Doctor dry run" in summary
        assert "Doctorable failed fixtures: 0" in summary
        # Zero-pass info is not in per-file dry-run — it's shown consolidated
        assert "100%-failure" not in summary


class TestBuildZeroPassTargets:
    def test_zero_pass_models_generate_full_benchmark_targets(self):
        payload = {
            "profiles": [
                {
                    "profile": "p",
                    "models": [
                        {
                            "model": "dead",
                            "summary": {"total_fixtures": 3, "total_passed": 0, "overall_pass_at_k": 0.0},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "total": 3,
                                    "passed": 0,
                                    "errors": 3,
                                    "scores": [
                                        {"fixture_id": "fx", "passed": False, "error": "x"},
                                        {"fixture_id": "fy", "passed": False, "error": "y"},
                                        {"fixture_id": "fz", "passed": False, "error": "z"},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        targets = build_zero_pass_targets(payload)
        assert len(targets) == 1
        assert targets[0].profile == "p"
        assert targets[0].model == "dead"
        assert targets[0].benchmark == "bm"
        assert set(targets[0].fixture_ids) == {"fx", "fy", "fz"}

    def test_zero_pass_fixtures_generate_targets_per_model_benchmark(self):
        payload = {
            "profiles": [
                {
                    "profile": "p",
                    "models": [
                        {
                            "model": "m1",
                            "summary": {"total_fixtures": 3, "total_passed": 1},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {"fixture_id": "fx", "passed": True, "error": None},
                                        {"fixture_id": "fy", "passed": False, "error": "bad"},
                                        {"fixture_id": "fz", "passed": False, "error": "bad"},
                                    ],
                                }
                            ],
                        },
                        {
                            "model": "m2",
                            "summary": {"total_fixtures": 3, "total_passed": 1},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {"fixture_id": "fx", "passed": True, "error": None},
                                        {"fixture_id": "fy", "passed": False, "error": "bad"},
                                        {"fixture_id": "fz", "passed": False, "error": "bad"},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        targets = build_zero_pass_targets(payload)
        # fy and fz are zero-pass (failed in both models)
        assert len(targets) == 2
        assert all(t.benchmark == "bm" for t in targets)
        for t in targets:
            assert set(t.fixture_ids) == {"fy", "fz"}

    def test_mixed_zero_pass_model_and_fixtures(self):
        payload = {
            "profiles": [
                {
                    "profile": "p",
                    "models": [
                        {
                            "model": "dead",
                            "summary": {"total_fixtures": 2, "total_passed": 0},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {"fixture_id": "fx", "passed": False, "error": "x"},
                                        {"fixture_id": "fy", "passed": False, "error": "y"},
                                    ],
                                }
                            ],
                        },
                        {
                            "model": "alive",
                            "summary": {"total_fixtures": 2, "total_passed": 1},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {"fixture_id": "fx", "passed": True, "error": None},
                                        {"fixture_id": "fy", "passed": False, "error": "y"},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        targets = build_zero_pass_targets(payload)
        # dead model: all fixtures get rerun
        # alive model + fy: fy is zero-pass (failed in both), gets rerun for alive
        assert len(targets) == 2
        dead_target = [t for t in targets if t.model == "dead"][0]
        alive_target = [t for t in targets if t.model == "alive"][0]
        assert set(dead_target.fixture_ids) == {"fx", "fy"}
        assert set(alive_target.fixture_ids) == {"fy"}

    def test_no_zero_pass_produces_empty_targets(self):
        payload = {
            "profiles": [
                {
                    "profile": "p",
                    "models": [
                        {
                            "model": "good",
                            "summary": {"total_fixtures": 1, "total_passed": 1},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {"fixture_id": "fx", "passed": True, "error": None},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        assert build_zero_pass_targets(payload) == []

    def test_retry_marker_is_scoped_to_model_and_benchmark(self):
        payload = {
            "profiles": [
                {
                    "profile": "p",
                    "models": [
                        {
                            "model": "m1",
                            "summary": {"total_fixtures": 2, "total_passed": 0},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {
                                            "fixture_id": "f001",
                                            "passed": False,
                                            "error": "bad",
                                            "_doctor_retried": True,
                                        },
                                    ],
                                }
                            ],
                        },
                        {
                            "model": "m2",
                            "summary": {"total_fixtures": 2, "total_passed": 0},
                            "results": [
                                {
                                    "benchmark": "bm",
                                    "scores": [
                                        {
                                            "fixture_id": "f001",
                                            "passed": False,
                                            "error": "bad",
                                        },
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }

        targets = build_zero_pass_targets(payload)

        assert [(t.model, t.fixture_ids) for t in targets] == [("m2", ("f001",))]


def test_benchmark_level_doctorable_error_reruns_all_benchmark_fixtures():
    payload = {
        "profiles": [
            {
                "profile": "openrouter",
                "models": [
                    {
                        "model": "anthropic/claude-opus-4.7:high",
                        "summary": {"total_fixtures": 0, "total_passed": 0},
                        "results": [
                            {
                                "benchmark": "git_grep",
                                "error": "[Errno 24] Too many open files",
                                "total": 0,
                                "passed": 0,
                                "errors": 0,
                                "pass_at_k": 0.0,
                            }
                        ],
                    },
                ],
            }
        ],
    }

    plan = build_rerun_plan(payload)

    assert plan.doctorable_count == 12
    assert plan.targets == [
        type(plan.targets[0])(
            "openrouter",
            "anthropic/claude-opus-4.7:high",
            "git_grep",
            tuple(f"f{i:03d}" for i in range(1, 13)),
        )
    ]
    assert plan.pattern_counts == {"[Errno 24] Too many open files": 12}
