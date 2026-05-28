"""Tests for fixture self-check validation."""

import subprocess

from gitbench.fixture_self_check import check_fixture
from gitbench.harness.types import Fixture


def test_self_check_flags_non_hash_expected_for_hash_prompt():
    fixture = Fixture(
        id="hash_bad",
        description="Bad hash fixture",
        setup=[],
        prompt="What is the short hash for Fix null pointer bug?",
        expected="Fix null pointer bug",
        scoring={"type": "exact_match"},
    )

    issues = check_fixture(fixture)

    assert [issue.code for issue in issues] == ["static-non-hash-expected"]


def test_self_check_allows_dynamic_hash_scorer_for_hash_prompt():
    fixture = Fixture(
        id="hash_ok",
        description="Dynamic hash fixture",
        setup=[],
        prompt="What is the short hash for Fix null pointer bug?",
        expected="",
        scoring={"type": "commit_hash_by_subject", "subject": "Fix null pointer bug"},
    )

    assert check_fixture(fixture) == []


def test_self_check_flags_multiline_exact_match_without_order_contract():
    fixture = Fixture(
        id="lines_bad",
        description="Line list fixture",
        setup=[],
        prompt="List matching messages",
        expected="A\nB",
        scoring={"type": "exact_match"},
    )

    issues = check_fixture(fixture)

    assert [issue.code for issue in issues] == ["multiline-exact-order-review"]


def test_self_check_allows_multiline_exact_match_with_order_contract():
    fixture = Fixture(
        id="lines_ok",
        description="Ordered line list fixture",
        setup=[],
        prompt="List matching messages in reverse chronological order",
        expected="B\nA",
        scoring={"type": "exact_match", "order_matters": True},
    )

    assert check_fixture(fixture) == []


def test_self_check_validates_git_derived_expected_value(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    fixture = Fixture(
        id="derived_ok",
        description="Derived fixture",
        setup=[],
        prompt="How many tracked files exist?",
        expected="0",
        scoring={
            "type": "numeric_exact",
            "self_check": {
                "command": "git ls-files",
                "transform": "count_nonempty_lines",
            },
        },
    )

    assert check_fixture(fixture, repo_path=str(repo)) == []


def test_self_check_reports_git_derived_expected_mismatch(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    fixture = Fixture(
        id="derived_bad",
        description="Derived fixture",
        setup=[],
        prompt="How many tracked files exist?",
        expected="1",
        scoring={
            "type": "numeric_exact",
            "self_check": {
                "command": "git ls-files",
                "transform": "count_nonempty_lines",
            },
        },
    )

    issues = check_fixture(fixture, repo_path=str(repo))

    assert [issue.code for issue in issues] == ["derived-expected-mismatch"]
