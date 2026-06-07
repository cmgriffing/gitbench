"""Tests for gitbench.harness.reasoning model-name parsing module."""

from gitbench.harness.reasoning import (
    VALID_REASONING_LEVELS,
    parse_model_reasoning,
)


class TestParseModelReasoning:
    def test_bare_name(self):
        base, level = parse_model_reasoning("gpt-4o")
        assert base == "gpt-4o"
        assert level is None

    def test_with_reasoning_level(self):
        base, level = parse_model_reasoning("o3-mini#high")
        assert base == "o3-mini"
        assert level == "high"

    def test_multiple_hash_uses_last(self):
        base, level = parse_model_reasoning("model#extra#low")
        assert base == "model#extra"
        assert level == "low"

    def test_mock_model_bypasses_parsing(self):
        base, level = parse_model_reasoning("mock#high")
        assert base == "mock"
        assert level == "high"

    def test_empty_level(self):
        base, level = parse_model_reasoning("model#")
        assert base == "model"
        assert level == ""

    def test_no_hash(self):
        base, level = parse_model_reasoning("llama3.1:8b")
        assert base == "llama3.1:8b"
        assert level is None

    def test_colon_effort(self):
        base, level = parse_model_reasoning("anthropic/claude-opus-4.7:max")
        assert base == "anthropic/claude-opus-4.7"
        assert level == "max"

    def test_colon_model_tag_with_effort(self):
        base, level = parse_model_reasoning("llama3.1:8b:high")
        assert base == "llama3.1:8b"
        assert level == "high"

    def test_provider_prefix_with_level(self):
        base, level = parse_model_reasoning("openai/gpt-4o#high")
        assert base == "openai/gpt-4o"
        assert level == "high"

    def test_colon_in_model_name(self):
        base, level = parse_model_reasoning("anthropic/claude-3.5:latest#medium")
        assert base == "anthropic/claude-3.5:latest"
        assert level == "medium"


class TestValidReasoningLevels:
    def test_expected_levels(self):
        assert VALID_REASONING_LEVELS == ["none", "minimal", "low", "medium", "high", "xhigh", "max"]

    def test_level_count(self):
        assert len(VALID_REASONING_LEVELS) == 7
