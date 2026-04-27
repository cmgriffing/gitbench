"""Worktree usage benchmark for GitBench."""

import logging
import os
import subprocess
from pathlib import Path

from gitbench.benchmarks import Benchmark
from gitbench.harness.loader import FixtureLoader
from gitbench.harness.scorer import Scorer
from gitbench.harness.types import Fixture, Score
from gitbench.utils.git import GitExecutor

logger = logging.getLogger(__name__)


class WorktreeUsageBenchmark(Benchmark):
    """Benchmark for evaluating LLM git worktree usage.

    This benchmark provides a repository and asks the model to perform
    git worktree operations. The model's output (commands) is executed
    in the repo, then state assertions are checked.
    """

    name = "worktree_usage"
    description = "Use git worktrees for parallel development"

    def __init__(self):
        """Initialize the worktree usage benchmark."""
        self._loader = FixtureLoader()
        self._scorer = Scorer()

    def load_fixtures(self) -> list[Fixture]:
        """Load all worktree usage fixtures.

        Returns:
            List of Fixture objects from the fixtures/worktree_usage directory.
        """
        fixtures_dir = Path(__file__).parent.parent.parent / "fixtures" / "worktree_usage"
        logger.info(f"Loading fixtures from: {fixtures_dir}")

        fixtures = self._loader.load_dir(str(fixtures_dir))
        logger.info(f"Loaded {len(fixtures)} fixtures")
        return fixtures

    def setup_fixture(self, fixture: Fixture) -> tuple[GitExecutor, str]:
        """Set up a git repository for a worktree scenario.

        Args:
            fixture: The fixture containing setup commands.

        Returns:
            A tuple of (GitExecutor, repo_path).
        """
        executor = GitExecutor()
        repo_path = executor.setup_repo(f"worktree_usage_{fixture.id}", fixture.setup)

        # Register sibling directories for cleanup (worktrees are created outside repo)
        parent_dir = os.path.dirname(repo_path)
        # Register common worktree paths that fixtures use
        for wt_name in ["feature-wt", "feature", "hotfix", "new-feature",
                        "detached-wt", "wt-a", "wt-b", "v1-checkout",
                        "feature-review"]:
            wt_path = os.path.join(parent_dir, wt_name)
            executor.register_cleanup(wt_path)

        logger.debug(f"Set up fixture {fixture.id} at {repo_path}")
        return executor, repo_path

    def score(self, fixture: Fixture, model_output: str, repo_path: str | None = None) -> Score:
        """Score the fixture by executing model output then checking state.

        Args:
            fixture: The fixture with expected state assertions.
            model_output: The git commands output by the model.
            repo_path: Path to the git repository.

        Returns:
            A Score object based on state assertion results.
        """
        if repo_path is None:
            return Score(
                fixture_id=fixture.id,
                passed=False,
                similarity=0.0,
                model_output=model_output,
                error="repo_path required for state_assertions scoring",
            )

        # Execute the model's commands
        self.execute_model_output(repo_path, model_output, fixture)

        # Score based on state assertions
        return self._scorer.score(fixture, model_output, repo_path=repo_path)

    def execute_model_output(self, repo_path: str, model_output: str, fixture: Fixture) -> None:
        """Execute the model's output as shell commands.

        Runs each line as a command. Stops on first failure.

        Args:
            repo_path: Path to the git repository.
            model_output: The model's command output.
            fixture: The fixture being scored.
        """
        lines = [line.strip() for line in model_output.strip().split("\n") if line.strip()]

        for line in lines:
            logger.info(f"Executing: {line}")
            try:
                result = subprocess.run(
                    line,
                    shell=True,
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    logger.warning(
                        f"Command failed (exit {result.returncode}): {line}\n"
                        f"stderr: {result.stderr}"
                    )
                    # Stop on failure
                    return
                if result.stderr:
                    logger.debug(f"Command stderr: {result.stderr}")
            except subprocess.TimeoutExpired:
                logger.error(f"Command timed out: {line}")
                return
            except Exception as e:
                logger.error(f"Command error: {line}: {e}")
                return

    def get_diff(self, repo_path: str) -> str:
        """Get the current branch and worktree status.

        Args:
            repo_path: Path to the git repository.

        Returns:
            Git branch and worktree list output.
        """
        branch_result = subprocess.run(
            ["git", "branch", "-v"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        worktree_result = subprocess.run(
            ["git", "worktree", "list"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        output = f"Branches:\n{branch_result.stdout}\n"
        output += f"Worktrees:\n{worktree_result.stdout}"
        return output

    def format_prompt(self, fixture: Fixture, diff: str) -> str:
        """Format the prompt with the fixture prompt and repo status.

        Args:
            fixture: The fixture containing the base prompt.
            diff: The git branch/worktree output to include.

        Returns:
            The formatted prompt string.
        """
        return f"{fixture.prompt}\n\n{diff}"
