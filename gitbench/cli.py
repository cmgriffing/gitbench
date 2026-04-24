"""CLI for GitBench."""

import json
import logging
import shutil
import sys
from pathlib import Path

import click

from gitbench.harness.model import MockModelClient, OpenAIAdapter
from gitbench.harness.types import BenchmarkResult, ModelMessage, Score

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def check_git_availability() -> bool:
    """Check if git CLI is available.

    Returns:
        True if git is available, False otherwise.
    """
    git_path = shutil.which("git")
    if git_path:
        logger.info(f"Git CLI found at: {git_path}")
        return True
    else:
        logger.error("Git CLI not found in PATH")
        return False


def get_model_client(model_type: str) -> OpenAIAdapter | MockModelClient:
    """Get the model client based on type.

    Args:
        model_type: Either 'openai' or 'mock'.

    Returns:
        The appropriate model client instance.

    Raises:
        click.ClickException: If model type is invalid.
    """
    if model_type == "openai":
        return OpenAIAdapter()
    elif model_type == "mock":
        return MockModelClient()
    else:
        raise click.ClickException(
            f"Unknown model type: {model_type}. Use 'openai' or 'mock'."
        )


@click.group()
def cli():
    """GitBench: Benchmark harness for evaluating LLM-generated git commit messages."""
    pass


@cli.command()
@click.option(
    "--benchmark",
    "-b",
    required=True,
    help="Name of the benchmark to run",
)
@click.option(
    "--model",
    "-m",
    default="mock",
    type=click.Choice(["mock", "openai"]),
    help="Model type to use (default: mock)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (writes JSON, defaults to stdout)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Print detailed per-fixture results",
)
def run(benchmark: str, model: str, output: str | None, verbose: bool):
    """Run a benchmark against the specified model."""
    # Check git availability on startup
    if not check_git_availability():
        click.echo("Error: Git CLI is required but not found in PATH", err=True)
        sys.exit(1)

    logger.info(f"Starting benchmark: {benchmark} with model: {model}")
    click.echo(f"Running benchmark '{benchmark}' with model '{model}'...")

    try:
        model_client = get_model_client(model)

        # For now, create a simple mock result structure
        # TODO: Integrate with actual benchmark runner
        scores = [
            Score(
                fixture_id="test_001",
                passed=False,
                similarity=0.0,
                model_output="",
                error="Benchmark runner not yet implemented",
            )
        ]

        result = BenchmarkResult(
            benchmark=benchmark,
            total=1,
            passed=0,
            pass_at_k=0.0,
            scores=scores,
            errors=1,
        )

        # Output results
        output_dict = result.to_dict()

        if verbose:
            click.echo("\nPer-fixture results:")
            for score in result.scores:
                click.echo(f"  {score.fixture_id}: passed={score.passed}, similarity={score.similarity}")
                if score.error:
                    click.echo(f"    Error: {score.error}")
                if score.model_output:
                    click.echo(f"    Output: {score.model_output[:100]}...")

        output_json = json.dumps(output_dict, indent=2)

        if output:
            Path(output).write_text(output_json)
            click.echo(f"\nResults written to: {output}")
        else:
            click.echo(output_json)

        logger.info(f"Benchmark completed: {result.passed}/{result.total} passed")

    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("list")
def list_benchmarks():
    """List available benchmarks."""
    # Check git availability
    if not check_git_availability():
        click.echo("Warning: Git CLI not found - some benchmarks may not work", err=True)

    available = ["commit_messages"]

    click.echo("Available benchmarks:")
    for benchmark in available:
        click.echo(f"  - {benchmark}")


if __name__ == "__main__":
    cli()