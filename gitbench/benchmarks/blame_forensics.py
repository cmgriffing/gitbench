"""Blame/forensics benchmark for GitBench."""

import logging
import subprocess
from pathlib import Path

from gitbench.benchmarks import Benchmark
from gitbench.harness.loader import FixtureLoader
from gitbench.harness.scorer import Scorer
from gitbench.harness.types import Fixture, Score
from gitbench.utils.git import GitExecutor

logger = logging.getLogger(__name__)


class BlameForensicsBenchmark(Benchmark):
    """Benchmark for evaluating LLM git blame and forensics reasoning.

    This benchmark sets up a repository with a bug introduced in a specific
    commit and asks the model to trace which commit introduced the bug
    using git log and git blame. Scored via exact_match on commit message.
    """

    name = "blame_forensics"
    description = "Trace which commit introduced a bug using git blame/log"

    def __init__(self):
        """Initialize the blame forensics benchmark."""
        self._loader = FixtureLoader()
        self._scorer = Scorer()

    def load_fixtures(self) -> list[Fixture]:
        """Load all blame forensics fixtures.

        Returns:
            List of Fixture objects from the fixtures/blame_forensics directory.
        """
        fixtures_dir = Path(__file__).parent.parent.parent / "fixtures" / "blame_forensics"
        logger.info(f"Loading fixtures from: {fixtures_dir}")

        fixtures = self._loader.load_dir(str(fixtures_dir))
        logger.info(f"Loaded {len(fixtures)} fixtures")
        return fixtures

    def score(self, fixture: Fixture, model_output: str, repo_path: str | None = None) -> Score:
        """Score a blame answer against the expected value.

        Args:
            fixture: The fixture containing the expected commit message.
            model_output: The commit message identified by the model.
            repo_path: Optional path to the git repository (unused).

        Returns:
            A Score object with passed/failed status and similarity value.
        """
        return self._scorer.score(fixture, model_output, repo_path=repo_path)

    def setup_fixture(self, fixture: Fixture) -> tuple[GitExecutor, str]:
        """Set up a git repository for a blame forensics scenario.

        Args:
            fixture: The fixture containing setup commands.

        Returns:
            A tuple of (GitExecutor, repo_path).
        """
        executor = GitExecutor()
        repo_path = executor.setup_repo(f"blame_forensics_{fixture.id}", fixture.setup)
        logger.debug(f"Set up fixture {fixture.id} at {repo_path}")
        return executor, repo_path

    def get_diff(self, repo_path: str) -> str:
        """Get git log and blame output for the repository.

        Returns git log (all commits) and git blame on the relevant source file.

        Args:
            repo_path: Path to the git repository.

        Returns:
            Git log + blame output for analysis.
        """
        # Get git log
        log_result = subprocess.run(
            ["git", "log", "--oneline", "--all"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        # Try to find source files for blame
        files_result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        output = f"Git log:\n{log_result.stdout}\n"

        # Run blame on each source file
        if files_result.stdout.strip():
            for file_path in files_result.stdout.strip().split("\n"):
                if file_path:
                    blame_result = subprocess.run(
                        ["git", "blame", file_path],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                    )
                    if blame_result.returncode == 0:
                        output += f"\nGit blame {file_path}:\n{blame_result.stdout}"

        return output

    def format_prompt(self, fixture: Fixture, diff: str) -> str:
        """Format the prompt with the fixture prompt and git history.

        Args:
            fixture: The fixture containing the base prompt.
            diff: The git log + blame output to include in the prompt.

        Returns:
            The formatted prompt string.
        """
        return f"{fixture.prompt}\n\n{diff}"
