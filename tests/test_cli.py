"""Tests for GitBench CLI."""

import json
import sys
from io import StringIO
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gitbench.cli import cli, check_git_availability, get_model_client


@pytest.fixture
def runner():
    """Create a Click test runner."""
    return CliRunner()


class TestCheckGitAvailability:
    """Tests for check_git_availability function."""

    def test_returns_true_when_git_available(self):
        """Test that function returns True when git is found."""
        with patch("shutil.which", return_value="/usr/bin/git"):
            result = check_git_availability()
            assert result is True

    def test_returns_false_when_git_not_available(self):
        """Test that function returns False when git is not found."""
        with patch("shutil.which", return_value=None):
            result = check_git_availability()
            assert result is False


class TestGetModelClient:
    """Tests for get_model_client function."""

    def test_returns_mock_client(self):
        """Test that 'mock' returns a MockModelClient."""
        client = get_model_client("mock")
        from gitbench.harness.model import MockModelClient
        assert isinstance(client, MockModelClient)

    def test_returns_openai_adapter(self):
        """Test that 'openai' returns an OpenAIAdapter."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
            client = get_model_client("openai")
            from gitbench.harness.model import OpenAIAdapter
            assert isinstance(client, OpenAIAdapter)

    def test_raises_on_invalid_model_type(self):
        """Test that invalid model type raises ClickException."""
        from click import ClickException
        with pytest.raises(ClickException):
            get_model_client("invalid_model")


class TestListCommand:
    """Tests for the list command."""

    def test_list_shows_benchmarks(self, runner):
        """Test that list shows available benchmarks."""
        with patch("gitbench.cli.check_git_availability", return_value=True):
            result = runner.invoke(cli, ["list"])
            assert result.exit_code == 0
            assert "commit_messages" in result.output

    def test_list_warns_when_git_missing(self, runner):
        """Test that list warns when git is not available."""
        with patch("gitbench.cli.check_git_availability", return_value=False):
            result = runner.invoke(cli, ["list"])
            assert "Warning" in result.output or "not found" in result.output


class TestRunCommand:
    """Tests for the run command."""

    def test_run_requires_benchmark_option(self, runner):
        """Test that run command requires --benchmark option."""
        result = runner.invoke(cli, ["run"])
        assert result.exit_code != 0
        assert "--benchmark" in result.output or "Missing" in result.output

    def test_run_with_mock_model(self, runner):
        """Test running with mock model produces JSON output."""
        with patch("gitbench.cli.check_git_availability", return_value=True):
            result = runner.invoke(
                cli,
                ["run", "--benchmark", "commit_messages", "--model", "mock"],
            )
            assert result.exit_code == 0

            # Output should be valid JSON - try to find JSON in output
            # The CLI outputs JSON to stdout, possibly with additional echo statements
            output = result.output.strip()

            # Try to find JSON object in output (may be surrounded by other text)
            json_start = output.find("{")
            if json_start != -1:
                # Find the matching closing brace
                json_candidate = output[json_start:]
                brace_count = 0
                json_end = len(json_candidate)
                for i, char in enumerate(json_candidate):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break

                json_str = json_candidate[:json_end]
                data = json.loads(json_str)
                assert "benchmark" in data
                assert data["benchmark"] == "commit_messages"
            else:
                pytest.fail(f"No JSON found in output: {output}")

    def test_run_with_output_file(self, runner, tmp_path):
        """Test that run can write to output file."""
        output_path = tmp_path / "results.json"

        with patch("gitbench.cli.check_git_availability", return_value=True):
            result = runner.invoke(
                cli,
                ["run", "--benchmark", "commit_messages", "--model", "mock", "--output", str(output_path)],
            )
            assert result.exit_code == 0

            # Check file was created and contains valid JSON
            content = output_path.read_text()
            data = json.loads(content)
            assert "benchmark" in data

    def test_run_with_verbose_flag(self, runner):
        """Test that verbose flag shows per-fixture results."""
        with patch("gitbench.cli.check_git_availability", return_value=True):
            result = runner.invoke(
                cli,
                ["run", "--benchmark", "commit_messages", "--model", "mock", "--verbose"],
            )
            assert result.exit_code == 0
            # Verbose output should mention per-fixture or similar
            assert "Per-fixture" in result.output or "fixture" in result.output.lower()

    def test_run_exits_with_error_when_git_missing(self, runner):
        """Test that run exits with error when git is not available."""
        with patch("gitbench.cli.check_git_availability", return_value=False):
            result = runner.invoke(
                cli,
                ["run", "--benchmark", "commit_messages", "--model", "mock"],
            )
            assert result.exit_code == 1
            assert "Git" in result.output or "git" in result.output