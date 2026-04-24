"""Git reflog benchmark for GitBench."""

import logging
import subprocess
from pathlib import Path

from gitbench.benchmarks import Benchmark
from gitbench.harness.loader import FixtureLoader
from gitbench.harness.scorer import Scorer
from gitbench.harness.types import Fixture, Score
from gitbench.utils.git import GitExecutor

logger = logging.getLogger(__name__)


class ReflogBenchmark(Benchmark):
    """Benchmark for evaluating git reflog reasoning.

    This benchmark sets up a real git repository with a scenario where
    commits have been lost (reset, rebase, amend) and asks the model
    to identify the correct commit state or recovery instruction using
    git reflog output.
    """

    name = "reflog"
    description = "Recover lost commits using git reflog"

    def __init__(self):
        """Initialize the reflog benchmark."""
        self._loader = FixtureLoader()
        self._scorer = Scorer()

    def load_fixtures(self) -> list[Fixture]:
        """Load all git reflog fixtures.

        Returns:
            List of Fixture objects from the fixtures/reflog directory.

        Raises:
            FileNotFoundError: If the fixtures directory doesn't exist.
        """
        fixtures_dir = Path(__file__).parent.parent.parent / "fixtures" / "reflog"
        logger.info(f"Loading fixtures from: {fixtures_dir}")

        fixtures = self._loader.load_dir(str(fixtures_dir))
        logger.info(f"Loaded {len(fixtures)} fixtures")
        return fixtures

    def score(self, fixture: Fixture, model_output: str) -> Score:
        """Score the model's recovery answer against the expected value.

        Args:
            fixture: The fixture containing the expected recovery answer.
            model_output: The commit hash or recovery instruction produced by the model.

        Returns:
            A Score object with passed/failed status and similarity value.
        """
        return self._scorer.score(fixture, model_output)

    def setup_fixture(self, fixture: Fixture) -> tuple[GitExecutor, str]:
        """Set up a git repository for a reflog recovery scenario.

        Args:
            fixture: The fixture containing setup commands.

        Returns:
            A tuple of (GitExecutor, repo_path).

        Raises:
            RuntimeError: If setup commands fail.
        """
        executor = GitExecutor()
        repo_path = executor.setup_repo(f"reflog_{fixture.id}", fixture.setup)
        logger.debug(f"Set up fixture {fixture.id} at {repo_path}")
        return executor, repo_path

    def get_diff(self, repo_path: str) -> str:
        """Get git reflog output for the repository.

        Returns the reflog showing all reference updates including
        commits that have been lost from the main history but are
        still reachable via reflog. This gives the model the information
        needed to identify the correct commit to recover.

        Args:
            repo_path: Path to the git repository.

        Returns:
            Git reflog output showing commit history including lost commits.
        """
        result = subprocess.run(
            ["git", "reflog", "show", "--no-abbrev"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"git reflog show --no-abbrev failed: {result.stderr}")
            # Fall back to simple reflog
            result = subprocess.run(
                ["git", "reflog"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logger.error(f"git reflog failed: {result.stderr}")
                return ""

        return result.stdout

    def format_prompt(self, fixture: Fixture, diff: str) -> str:
        """Format the prompt with the fixture prompt and git reflog output.

        Args:
            fixture: The fixture containing the base prompt.
            diff: The git reflog output to include in the prompt.

        Returns:
            The formatted prompt string.
        """
        return f"{fixture.prompt}\n\nGit reflog:\n{diff}"
