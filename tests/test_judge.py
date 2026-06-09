"""Tests for JudgeClient."""

from unittest.mock import MagicMock

import pytest

from gitbench.harness.judge import JUDGE_COMMIT_MESSAGE_PROMPT, JudgeClient
from gitbench.harness.types import ModelMessage


class TestJudgeClient:
    """Tests for JudgeClient class."""

    @pytest.fixture
    def mock_model(self):
        """Create a mock model client."""
        return MagicMock()

    @pytest.fixture
    def judge(self, mock_model):
        """Create a JudgeClient with a mock model."""
        return JudgeClient(mock_model)

    def test_init_accepts_model_interface(self, mock_model):
        """JudgeClient stores the model client."""
        judge = JudgeClient(mock_model)
        assert judge._model_client is mock_model

    def test_evaluate_commit_message_returns_float(self, judge, mock_model):
        """Judge returns a float score for a valid response."""
        mock_model.generate.return_value = {"text": "0.85", "content": "0.85"}

        score = judge.evaluate_commit_message("diff content", "Add feature X")

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_evaluate_commit_message_calls_model_with_prompt(self, judge, mock_model):
        """Judge constructs the correct prompt and calls the model."""
        mock_model.generate.return_value = {"text": "0.9"}

        judge.evaluate_commit_message("git diff --staged", "feat: add login")

        mock_model.generate.assert_called_once()
        call_args = mock_model.generate.call_args[0][0]
        assert len(call_args) == 1
        assert isinstance(call_args[0], ModelMessage)
        assert "git diff --staged" in call_args[0].content
        assert "feat: add login" in call_args[0].content
        assert "Score:" in call_args[0].content

    def test_evaluate_commit_message_high_score(self, judge, mock_model):
        """Judge returns high score for a good response."""
        mock_model.generate.return_value = {"text": "0.95", "content": "0.95"}

        score = judge.evaluate_commit_message(
            "Add hello.txt with greeting", "Add hello.txt with greeting message"
        )

        assert score == 0.95

    def test_evaluate_commit_message_low_score(self, judge, mock_model):
        """Judge returns low score for a bad response."""
        mock_model.generate.return_value = {"text": "0.1", "content": "0.1"}

        score = judge.evaluate_commit_message(
            "Add hello.txt with greeting", "Fix login bug"
        )

        assert score == 0.1

    def test_evaluate_commit_message_medium_score(self, judge, mock_model):
        """Judge returns medium score for a vague response."""
        mock_model.generate.return_value = {"text": "0.4", "content": "0.4"}

        score = judge.evaluate_commit_message(
            "Add three files: config.py, main.py, utils.py", "Update files"
        )

        assert score == 0.4

    def test_evaluate_commit_message_parses_integer_score(self, judge, mock_model):
        """Judge parses integer scores (0 or 1)."""
        mock_model.generate.return_value = {"text": "1", "content": "1"}

        score = judge.evaluate_commit_message("diff", "perfect message")

        assert score == 1.0

    def test_evaluate_commit_message_parses_score_with_text(self, judge, mock_model):
        """Judge extracts score from response with surrounding text."""
        mock_model.generate.return_value = {
            "text": "The score is 0.75 because the message is good.",
            "content": "The score is 0.75 because the message is good.",
        }

        score = judge.evaluate_commit_message("diff", "message")

        assert score == 0.75

    def test_evaluate_commit_message_clamps_below_zero(self, judge, mock_model):
        """Judge clamps scores below 0.0 to 0.0."""
        mock_model.generate.return_value = {"text": "-0.5"}

        score = judge.evaluate_commit_message("diff", "message")

        assert score == 0.0

    def test_evaluate_commit_message_clamps_above_one(self, judge, mock_model):
        """Judge clamps scores above 1.0 to 1.0."""
        mock_model.generate.return_value = {"text": "1.5"}

        score = judge.evaluate_commit_message("diff", "message")

        assert score == 1.0

    def test_evaluate_commit_message_handles_string_response(self, judge, mock_model):
        """Judge handles plain string responses from model."""
        mock_model.generate.return_value = "0.8"

        score = judge.evaluate_commit_message("diff", "message")

        assert score == 0.8

    def test_evaluate_commit_message_raises_on_non_numeric(self, judge, mock_model):
        """Judge raises ValueError when response has no number."""
        mock_model.generate.return_value = {"text": "This is a great message!"}

        with pytest.raises(ValueError, match="could not be parsed as a number"):
            judge.evaluate_commit_message("diff", "message")

    def test_evaluate_commit_message_raises_on_empty_response(self, judge, mock_model):
        """Judge raises ValueError when response is empty."""
        mock_model.generate.return_value = {"text": ""}

        with pytest.raises(ValueError, match="could not be parsed as a number"):
            judge.evaluate_commit_message("diff", "message")

    def test_evaluate_commit_message_retries_once_on_failure(self, judge, mock_model):
        """Judge retries once when first call fails and second succeeds."""
        mock_model.generate.side_effect = [
            RuntimeError("Temporary failure"),
            {"text": "0.7"},
        ]

        score = judge.evaluate_commit_message("diff", "message")

        assert score == 0.7
        assert mock_model.generate.call_count == 2

    def test_evaluate_commit_message_raises_after_retry_failure(self, judge, mock_model):
        """Judge raises ValueError when both attempts fail."""
        mock_model.generate.side_effect = [
            RuntimeError("First failure"),
            RuntimeError("Second failure"),
        ]

        with pytest.raises(ValueError, match="Judge call failed after retry"):
            judge.evaluate_commit_message("diff", "message")

        assert mock_model.generate.call_count == 2

    def test_parse_score_extracts_first_number(self, judge):
        """_parse_score extracts the first numeric value."""
        result = judge._parse_score("0.67 is the score")
        assert result == 0.67

    def test_parse_score_handles_leading_zeros(self, judge):
        """_parse_score handles scores with leading zeros."""
        result = judge._parse_score("Score: 0.05")
        assert result == 0.05

    def test_judge_prompt_includes_diff_and_message(self):
        """The judge prompt template contains placeholders for diff and message."""
        prompt = JUDGE_COMMIT_MESSAGE_PROMPT.format(diff="DIFF", message="MSG")
        assert "DIFF" in prompt
        assert "MSG" in prompt
        assert "Score:" in prompt
