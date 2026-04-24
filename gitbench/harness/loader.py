"""Fixture loader for GitBench benchmarks."""

import logging
from pathlib import Path
from typing import Any

import yaml

from gitbench.harness.types import Fixture

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ("id", "setup", "prompt", "expected")


class FixtureLoader:
    """Loads and validates fixture files for benchmarking."""

    def load_file(self, path: str) -> list[Fixture]:
        """Parse a single YAML fixture file.

        Args:
            path: Path to the YAML fixture file.

        Returns:
            List of Fixture objects parsed from the file.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If a fixture is missing required fields or has invalid structure.
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Fixture file not found: {path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            logger.warning(f"Empty fixture file: {path}")
            return []

        # Support both single fixture (dict) and list of fixtures
        if isinstance(data, dict):
            fixtures = [data]
        elif isinstance(data, list):
            fixtures = data
        else:
            raise ValueError(f"Invalid fixture format in {path}: expected dict or list")

        results: list[Fixture] = []
        for idx, fixture_data in enumerate(fixtures):
            try:
                results.append(self._parse_fixture(fixture_data, path, idx))
            except ValueError as e:
                raise ValueError(f"Error in fixture at index {idx} of {path}: {e}") from e

        return results

    def _parse_fixture(self, data: Any, source: str, index: int) -> Fixture:
        """Parse and validate a single fixture dict.

        Args:
            data: Raw fixture dictionary.
            source: Source file path for error messages.
            index: Fixture index in file for error messages.

        Returns:
            Validated Fixture object.

        Raises:
            ValueError: If required fields are missing or types are wrong.
        """
        if not isinstance(data, dict):
            raise ValueError(f"Expected dict, got {type(data).__name__}")

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in data:
                raise ValueError(
                    f"Missing required field '{field}' in fixture {index} of {source}"
                )

        fixture_id = data["id"]
        if not isinstance(fixture_id, str) or not fixture_id.strip():
            raise ValueError(f"Fixture id must be a non-empty string in {source}:{index}")

        setup = data["setup"]
        if not isinstance(setup, list):
            raise ValueError(
                f"Fixture '{fixture_id}': 'setup' must be a list of strings"
            )
        for cmd in setup:
            if not isinstance(cmd, str):
                raise ValueError(
                    f"Fixture '{fixture_id}': each setup command must be a string"
                )

        prompt = data["prompt"]
        if not isinstance(prompt, str):
            raise ValueError(f"Fixture '{fixture_id}': 'prompt' must be a string")

        expected = data["expected"]
        if not isinstance(expected, str):
            raise ValueError(f"Fixture '{fixture_id}': 'expected' must be a string")

        scoring = data.get("scoring", {"type": "similarity", "threshold": 0.5})
        if not isinstance(scoring, dict):
            raise ValueError(
                f"Fixture '{fixture_id}': 'scoring' must be a dict"
            )

        description = data.get("description", "")

        return Fixture(
            id=fixture_id,
            description=description,
            setup=setup,
            prompt=prompt,
            expected=expected,
            scoring=scoring,
        )

    def load_dir(self, dirpath: str) -> list[Fixture]:
        """Load all YAML fixtures from a directory.

        Args:
            dirpath: Path to the directory containing fixture files.

        Returns:
            Combined list of all Fixture objects from all .yaml files.

        Raises:
            FileNotFoundError: If the directory does not exist.
        """
        dir_path = Path(dirpath)
        if not dir_path.is_dir():
            raise FileNotFoundError(f"Fixture directory not found: {dirpath}")

        all_fixtures: list[Fixture] = []

        for file_path in sorted(dir_path.iterdir()):
            if file_path.suffix.lower() in (".yaml", ".yml"):
                logger.debug(f"Loading fixtures from: {file_path}")
                try:
                    fixtures = self.load_file(str(file_path))
                    all_fixtures.extend(fixtures)
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {e}")
                    raise

        return all_fixtures
