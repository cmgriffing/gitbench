"""Git commit squash benchmark for GitBench."""

import logging
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

from gitbench.harness.loader import FixtureLoader
from gitbench.harness.scorer import Scorer
from gitbench.harness.types import Fixture, Score
from gitbench.utils.git import GitExecutor

logger = logging.getLogger(__name__)


class Benchmark(ABC):
    """Abstract base class for GitBench benchmarks."""

    name: str = ""
    description: str = ""

    @abstractmethod
    def load_fixtures(self) -> list[Fixture]:
        pass

    @abstractmethod
    def score(self, fixture: Fixture, model_output: str) -> Score:
        pass


class CommitSquashBenchmark(Benchmark):
    """Benchmark for evaluating git commit squash reasoning.

    This benchmark sets up a real git repository with a commit history
    that contains commits that should be squashed for cleaner history,
    and asks the model to identify which commits to squash.
    """

    name = "commit_squash"
    description = "Identify commits to squash into a cleaner history"

    def __init__(self):
        """Initialize the commit squash benchmark."""
        self._loader = FixtureLoader()
        self._scorer = Scorer()

    def load_fixtures(self) -> list[Fixture]:
        """Load all commit squash fixtures.

        Returns:
            List of Fixture objects from the fixtures/commit_squash directory.

        Raises:
            FileNotFoundError: If the fixtures directory doesn't exist.
        """
        fixtures_dir = Path(__file__).parent.parent.parent / "fixtures" / "commit_squash"
        logger.info(f"Loading fixtures from: {fixtures_dir}")

        fixtures = self._loader.load_dir(str(fixtures_dir))
        logger.info(f"Loaded {len(fixtures)} fixtures")
        return fixtures

    def score(self, fixture: Fixture, model_output: str) -> Score:
        """Score the model's identified commits to squash against the expected value.

        Args:
            fixture: The fixture containing the expected commits to squash.
            model_output: The commits or commit hashes to squash produced by the model.

        Returns:
            A Score object with passed/failed status and similarity value.
        """
        return self._scorer.score(fixture, model_output)

    def setup_fixture(self, fixture: Fixture) -> tuple[GitExecutor, str]:
        """Set up a git repository with a commit history for squash analysis.

        Args:
            fixture: The fixture containing setup commands.

        Returns:
            A tuple of (GitExecutor, repo_path).

        Raises:
            RuntimeError: If setup commands fail.
        """
        executor = GitExecutor()
        repo_path = executor.setup_repo(f"squash_{fixture.id}", fixture.setup)
        logger.debug(f"Set up fixture {fixture.id} at {repo_path}")
        return executor, repo_path

    def get_diff(self, repo_path: str) -> str:
        """Get git log output for the repository.

        Returns the commit log (newest first) showing the history
        that the model needs to analyze to identify commits to squash.

        Args:
            repo_path: Path to the git repository.

        Returns:
            Git log output showing commit history.
        """
        # Get commit log (newest first)
        result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"git log failed: {result.stderr}")
            return ""

        return result.stdout

    def format_prompt(self, fixture: Fixture, diff: str) -> str:
        """Format the prompt with the fixture prompt and git log output.

        Args:
            fixture: The fixture containing the base prompt.
            diff: The git log output to include in the prompt.

        Returns:
            The formatted prompt string.
        """
        return f"{fixture.prompt}\n\nGit commit history (newest first):\n{diff}"
