"""Scoring engine for GitBench benchmarks."""

import difflib
import logging
from typing import Any

from gitbench.harness.types import Fixture, Score

logger = logging.getLogger(__name__)


class Scorer:
    """Computes similarity scores for model outputs against expected values."""

    def score(self, fixture: Fixture, model_output: str) -> Score:
        """Score a model output against the expected value.

        Args:
            fixture: The fixture containing the expected output and scoring config.
            model_output: The string produced by the model.

        Returns:
            A Score object with passed/failed status and similarity value.

        Raises:
            ValueError: If the scoring type in the fixture is unsupported.
        """
        scoring = fixture.scoring
        scoring_type = scoring.get("type", "similarity")
        threshold = scoring.get("threshold", 0.5)

        try:
            if scoring_type == "similarity":
                similarity = difflib.SequenceMatcher(
                    None, model_output, fixture.expected
                ).ratio()
            else:
                raise ValueError(f"Unsupported scoring type: {scoring_type}")

            passed = similarity >= threshold

            return Score(
                fixture_id=fixture.id,
                passed=passed,
                similarity=round(similarity, 4),
                model_output=model_output,
                error=None,
            )
        except Exception as e:
            logger.error(f"Scoring error for fixture {fixture.id}: {e}")
            return Score(
                fixture_id=fixture.id,
                passed=False,
                similarity=0.0,
                model_output=model_output,
                error=f"Scoring error: {e}",
            )

    def pass_at_k(self, scores: list[Score], k: int = 1) -> float:
        """Compute pass@k metric.

        Args:
            scores: List of Score objects (one per fixture/attempt).
            k: Number of attempts considered per fixture.

        Returns:
            Fraction of fixtures where at least one of k attempts passed.
            Returns 0.0 if scores list is empty.
        """
        if not scores:
            return 0.0

        # Group scores by fixture_id
        from collections import defaultdict

        by_fixture: dict[str, list[Score]] = defaultdict(list)
        for s in scores:
            by_fixture[s.fixture_id].append(s)

        total_fixtures = len(by_fixture)
        passed_fixtures = 0

        for fixture_id, fixture_scores in by_fixture.items():
            # For each fixture, check if at least one score passed
            if any(s.passed for s in fixture_scores):
                passed_fixtures += 1

        return round(passed_fixtures / total_fixtures, 4)
