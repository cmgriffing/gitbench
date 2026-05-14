"""Tests for the scoring engine."""

import pytest

from gitbench.harness.scorer import Scorer
from gitbench.harness.types import Fixture, Score


class TestScorer:
    """Tests for Scorer class."""

    @pytest.fixture
    def scorer(self):
        """Create a Scorer instance."""
        return Scorer()

    @pytest.fixture
    def fixture_high_threshold(self):
        """Create a fixture with high threshold."""
        return Fixture(
            id="score_001",
            description="High threshold fixture",
            setup=["git init"],
            prompt="Generate commit message",
            expected="fix: correct spelling error in file.txt",
            scoring={"type": "similarity", "threshold": 0.7},
        )

    @pytest.fixture
    def fixture_default_threshold(self):
        """Create a fixture with default threshold (0.5)."""
        return Fixture(
            id="score_002",
            description="Default threshold fixture",
            setup=["git init"],
            prompt="Generate commit message",
            expected="feat: add new feature",
            scoring={"type": "similarity", "threshold": 0.5},
        )

    def test_score_exact_match(self, scorer, fixture_high_threshold):
        """Test that an exact match scores 1.0 and passes."""
        result = scorer.score(fixture_high_threshold, fixture_high_threshold.expected)

        assert result.passed is True
        assert result.similarity == 1.0
        assert result.fixture_id == "score_001"
        assert result.model_output == fixture_high_threshold.expected
        assert result.error is None

    def test_score_near_match_passes(self, scorer, fixture_high_threshold):
        """Test that a near-match output passes when above threshold."""
        output = "fix: correct spelling error in file.py"  # Very similar
        result = scorer.score(fixture_high_threshold, output)

        assert result.passed is True
        assert result.similarity > 0.7
        assert result.error is None

    def test_score_low_similarity_fails(self, scorer, fixture_high_threshold):
        """Test that low similarity output fails when below threshold."""
        output = "totally unrelated output that has nothing to do with commit messages"
        result = scorer.score(fixture_high_threshold, output)

        assert result.passed is False
        assert result.similarity < 0.7
        assert result.error is None

    def test_score_at_threshold_passes(self, scorer, fixture_high_threshold):
        """Test that output at exactly the threshold passes."""
        # Build an output with similarity >= 0.7
        output = "fix: correct spelling error"
        result = scorer.score(fixture_high_threshold, output)

        # Check it passes (ratio should be at least threshold)
        if result.similarity >= 0.7:
            assert result.passed is True
        else:
            assert result.passed is False

    def test_score_default_threshold(self, scorer, fixture_default_threshold):
        """Test that default threshold of 0.5 is used."""
        output = "feat: add feature"  # Similar but not exact
        result = scorer.score(fixture_default_threshold, output)

        # Should pass with 0.5 threshold
        assert result.passed is True
        assert result.similarity > 0.5

    def test_score_returns_score_object(self, scorer, fixture_high_threshold):
        """Test that score() returns a proper Score object."""
        result = scorer.score(fixture_high_threshold, "fix: typo")
        assert isinstance(result, Score)
        assert hasattr(result, "fixture_id")
        assert hasattr(result, "passed")
        assert hasattr(result, "similarity")
        assert hasattr(result, "model_output")
        assert hasattr(result, "error")

    def test_pass_at_k_single_attempt(self, scorer):
        """Test pass_at_k with single attempt per fixture."""
        scores = [
            Score(fixture_id="f1", passed=True, similarity=0.9, model_output="a", error=None),
            Score(fixture_id="f2", passed=False, similarity=0.3, model_output="b", error=None),
            Score(fixture_id="f3", passed=True, similarity=0.8, model_output="c", error=None),
        ]

        result = scorer.pass_at_k(scores, k=1)
        assert result == pytest.approx(0.6667)

    def test_pass_at_k_empty_list(self, scorer):
        """Test pass_at_k with empty list returns 0.0."""
        result = scorer.pass_at_k([], k=1)
        assert result == 0.0

    def test_pass_at_k_all_pass(self, scorer):
        """Test pass_at_k when all fixtures pass."""
        scores = [
            Score(fixture_id="f1", passed=True, similarity=0.9, model_output="a", error=None),
            Score(fixture_id="f2", passed=True, similarity=0.8, model_output="b", error=None),
        ]

        result = scorer.pass_at_k(scores, k=1)
        assert result == 1.0

    def test_pass_at_k_none_pass(self, scorer):
        """Test pass_at_k when no fixtures pass."""
        scores = [
            Score(fixture_id="f1", passed=False, similarity=0.2, model_output="a", error=None),
            Score(fixture_id="f2", passed=False, similarity=0.1, model_output="b", error=None),
        ]

        result = scorer.pass_at_k(scores, k=1)
        assert result == 0.0

    def test_pass_at_k_multiple_attempts(self, scorer):
        """Test pass_at_k with multiple attempts per fixture (k=2 scenario)."""
        # Fixture f1: attempt 1 fails, attempt 2 passes
        # Fixture f2: both attempts fail
        scores = [
            Score(fixture_id="f1", passed=False, similarity=0.3, model_output="a1", error=None),
            Score(fixture_id="f1", passed=True, similarity=0.8, model_output="a2", error=None),
            Score(fixture_id="f2", passed=False, similarity=0.2, model_output="b1", error=None),
            Score(fixture_id="f2", passed=False, similarity=0.1, model_output="b2", error=None),
        ]

        result = scorer.pass_at_k(scores, k=2)
        # f1 has at least one pass, f2 has none -> 1/2
        assert result == 0.5

    def test_pass_at_k_multiple_attempts_all_pass(self, scorer):
        """Test pass_at_k where each fixture has at least one pass among attempts."""
        scores = [
            Score(fixture_id="f1", passed=False, similarity=0.3, model_output="a1", error=None),
            Score(fixture_id="f1", passed=True, similarity=0.8, model_output="a2", error=None),
            Score(fixture_id="f2", passed=True, similarity=0.7, model_output="b1", error=None),
        ]

        result = scorer.pass_at_k(scores, k=3)
        assert result == 1.0

    def test_score_with_empty_output(self, scorer, fixture_default_threshold):
        """Test scoring with empty model output."""
        result = scorer.score(fixture_default_threshold, "")

        assert result.passed is False
        assert result.similarity == 0.0
        assert result.error is None

    def test_command_equivalence_single_command_matches(self, scorer):
        fixture = Fixture(
            id="cmd_001",
            description="Command equivalence fixture",
            setup=[],
            prompt="List worktrees",
            expected="",
            scoring={"type": "command_equivalence", "accepted": ["git worktree list"]},
        )

        result = scorer.score(fixture, "git worktree list")

        assert result.passed is True
        assert result.similarity == 1.0
        assert result.error is None

    def test_command_equivalence_accepts_equivalent_alternative(self, scorer):
        fixture = Fixture(
            id="cmd_002",
            description="Command equivalence fixture",
            setup=[],
            prompt="List submodules",
            expected="",
            scoring={
                "type": "command_equivalence",
                "accepted": ["git submodule", "git submodule status"],
            },
        )

        result = scorer.score(fixture, "git submodule status")

        assert result.passed is True
        assert result.similarity == 1.0

    def test_command_equivalence_normalizes_whitespace(self, scorer):
        fixture = Fixture(
            id="cmd_003",
            description="Command equivalence fixture",
            setup=[],
            prompt="List submodules",
            expected="",
            scoring={"type": "command_equivalence", "accepted": ["git submodule status"]},
        )

        result = scorer.score(fixture, "\n  git   submodule    status  \n\n")

        assert result.passed is True

    def test_command_equivalence_normalizes_quotes(self, scorer):
        fixture = Fixture(
            id="cmd_004",
            description="Command equivalence fixture",
            setup=[],
            prompt="Lock worktree",
            expected="",
            scoring={
                "type": "command_equivalence",
                "accepted": ["git worktree lock --reason 'do not delete' ../feature-wt"],
            },
        )

        result = scorer.score(
            fixture,
            'git worktree lock --reason "do not delete" ../feature-wt',
        )

        assert result.passed is True

    def test_command_equivalence_invalid_syntax_fails_with_error(self, scorer):
        fixture = Fixture(
            id="cmd_005",
            description="Command equivalence fixture",
            setup=[],
            prompt="List worktrees",
            expected="",
            scoring={"type": "command_equivalence", "accepted": ["git worktree list"]},
        )

        result = scorer.score(fixture, "git worktree list 'unterminated")

        assert result.passed is False
        assert result.similarity == 0.0
        assert "Could not parse model output" in result.error

    def test_command_equivalence_multi_command_sequence_matches(self, scorer):
        fixture = Fixture(
            id="cmd_006",
            description="Command equivalence fixture",
            setup=[],
            prompt="Initialize submodules",
            expected="",
            scoring={
                "type": "command_equivalence",
                "accepted": [["git submodule init", "git submodule update"]],
            },
        )

        result = scorer.score(fixture, "git submodule init\ngit submodule update")

        assert result.passed is True

    def test_command_equivalence_multi_command_alternative_matches(self, scorer):
        fixture = Fixture(
            id="cmd_007",
            description="Command equivalence fixture",
            setup=[],
            prompt="Initialize submodules",
            expected="",
            scoring={
                "type": "command_equivalence",
                "accepted": [
                    ["git submodule init", "git submodule update"],
                    ["git submodule update --init"],
                ],
            },
        )

        result = scorer.score(fixture, "git submodule update --init")

        assert result.passed is True

    def test_command_equivalence_wrong_command_order_fails(self, scorer):
        fixture = Fixture(
            id="cmd_008",
            description="Command equivalence fixture",
            setup=[],
            prompt="Initialize submodules",
            expected="",
            scoring={
                "type": "command_equivalence",
                "accepted": [["git submodule init", "git submodule update"]],
            },
        )

        result = scorer.score(fixture, "git submodule update\ngit submodule init")

        assert result.passed is False
        assert "Command did not match accepted alternatives" in result.error
