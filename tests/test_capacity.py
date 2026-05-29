"""Tests for capacity-aware request scheduling."""

import threading
import time

from gitbench.harness.benchmark import Benchmark
from gitbench.harness.capacity import (
    RequestBudgetCoordinator,
    derive_capacity_info,
    global_request_limit,
)
from gitbench.harness.runner import BenchmarkRunner
from gitbench.harness.types import Fixture, ModelMessage, Score


class _Cleanup:
    def cleanup(self) -> None:
        pass


class _SlowModel:
    reasoning_level = None

    def __init__(self) -> None:
        self.active = 0
        self.max_active = 0
        self.lock = threading.Lock()

    def generate(self, messages: list[ModelMessage], **kwargs):
        with self.lock:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
        try:
            time.sleep(0.05)
            return {"text": "ok", "usage": None}
        finally:
            with self.lock:
                self.active -= 1


class _FastBenchmark(Benchmark):
    name = "fast"
    description = "fast"

    def load_fixtures(self) -> list[Fixture]:
        return [
            Fixture(
                id=f"f{i}",
                description="fixture",
                setup=[],
                prompt="prompt",
                expected="ok",
                scoring={"type": "exact"},
            )
            for i in range(4)
        ]

    def setup_fixture(self, fixture: Fixture):
        return _Cleanup(), "/tmp"

    def get_diff(self, repo_path: str) -> str:
        return "diff"

    def score(self, fixture: Fixture, model_output: str, repo_path: str | None = None) -> Score:
        return Score(
            fixture_id=fixture.id,
            passed=True,
            similarity=1.0,
            model_output=model_output,
        )


def test_openrouter_anthropic_opus_versions_share_capacity_group():
    config = {}
    profile = {"base_url": "https://openrouter.ai/api/v1"}

    first = derive_capacity_info(config, profile, "anthropic/claude-opus-4.7:max")
    second = derive_capacity_info(config, profile, "anthropic/claude-opus-4.8:max")

    assert first.base_model_id == "anthropic/claude-opus-4.7"
    assert first.effort == "max"
    assert first.capacity_key == "openrouter:anthropic/claude-opus"
    assert second.capacity_key == "openrouter:anthropic/claude-opus"


def test_openrouter_inference_rules_and_fallback():
    profile = {"base_url": "https://openrouter.ai/api/v1"}

    assert (
        derive_capacity_info({}, profile, "anthropic/claude-sonnet-4.7:high").capacity_key
        == "openrouter:anthropic/claude-sonnet"
    )
    assert (
        derive_capacity_info({}, profile, "anthropic/claude-haiku-4.7:low").capacity_key
        == "openrouter:anthropic/claude-haiku"
    )
    assert (
        derive_capacity_info({}, profile, "openai/gpt-5.4-mini:high").capacity_key
        == "openrouter:openai/gpt-5"
    )
    assert (
        derive_capacity_info({}, profile, "google/gemini-3-pro:max").capacity_key
        == "openrouter:google/gemini-3"
    )
    assert (
        derive_capacity_info({}, profile, "mistral/devstral-small").capacity_key
        == "openrouter:mistral/devstral-small"
    )


def test_explicit_group_override_matches_base_model_after_effort_stripping():
    config = {
        "concurrency": {
            "groups": [
                {
                    "key": "openrouter:anthropic/claude",
                    "match": ["anthropic/claude-*"],
                    "max_concurrent_requests": 1,
                }
            ]
        }
    }
    profile = {
        "base_url": "https://openrouter.ai/api/v1",
        "max_concurrent_requests": 3,
    }

    info = derive_capacity_info(config, profile, "anthropic/claude-opus-4.7:max")

    assert info.capacity_key == "openrouter:anthropic/claude"
    assert info.request_limit == 1


def test_profile_request_limit_applies_when_group_has_no_limit():
    profile = {
        "provider": "openai",
        "max_concurrent_requests": 2,
    }

    info = derive_capacity_info({}, profile, "openai/gpt-5.4-mini:max")

    assert info.capacity_key == "openai:openai/gpt-5.4-mini"
    assert info.request_limit == 2


def test_global_request_limit_uses_config_before_fallback():
    assert global_request_limit({"concurrency": {"max_concurrent_requests": 4}}, fallback=8) == 4
    assert global_request_limit({}, fallback=8) == 8


def test_runner_gates_parallel_fixture_calls_by_group_budget():
    model = _SlowModel()
    budget = RequestBudgetCoordinator(
        global_limit=4,
        group_limits={"test:group": 1},
    )
    runner = BenchmarkRunner(
        {"fast": _FastBenchmark},
        model,
        request_budget=budget,
        capacity_key="test:group",
    )

    result = runner.run_benchmark("fast", fixture_workers=4)

    assert result.total == 4
    assert model.max_active == 1
