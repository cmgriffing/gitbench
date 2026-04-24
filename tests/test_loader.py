"""Tests for the fixture loader."""

from pathlib import Path

import pytest

from gitbench.harness.loader import FixtureLoader
from gitbench.harness.types import Fixture


class TestFixtureLoader:
    """Tests for FixtureLoader class."""

    def test_load_file_valid_single(self, tmp_path):
        """Test loading a valid YAML file with a single fixture."""
        yaml_content = (
            "id: commit_001\n"
            "description: Simple fix\n"
            "setup:\n"
            "  - git init\n"
            "  - echo hello world > file.txt\n"
            "  - git add .\n"
            "prompt: 'Generate a commit message for fixing a typo'\n"
            "expected: 'fix: correct typo in greeting'\n"
            "scoring:\n"
            "  type: similarity\n"
            "  threshold: 0.6\n"
        )

        fixture_file = tmp_path / "fixture.yaml"
        fixture_file.write_text(yaml_content)

        loader = FixtureLoader()
        fixtures = loader.load_file(str(fixture_file))

        assert len(fixtures) == 1
        f = fixtures[0]
        assert f.id == "commit_001"
        assert f.description == "Simple fix"
        assert f.setup == ["git init", "echo hello world > file.txt", "git add ."]
        assert f.prompt == "Generate a commit message for fixing a typo"
        assert f.expected == "fix: correct typo in greeting"
        assert f.scoring == {"type": "similarity", "threshold": 0.6}

    def test_load_file_valid_list(self, tmp_path):
        """Test loading a valid YAML file with a list of fixtures."""
        yaml_content = (
            "- id: commit_001\n"
            "  description: Simple fix\n"
            "  setup:\n"
            "    - git init\n"
            "  prompt: 'Fix typo'\n"
            "  expected: 'fix: typo'\n"
            "  scoring:\n"
            "    type: similarity\n"
            "    threshold: 0.5\n"
            "- id: commit_002\n"
            "  description: Feature add\n"
            "  setup:\n"
            "    - git init\n"
            "  prompt: 'Add feature'\n"
            "  expected: 'feat: add feature'\n"
            "  scoring:\n"
            "    type: similarity\n"
            "    threshold: 0.5\n"
        )

        fixture_file = tmp_path / "fixture.yaml"
        fixture_file.write_text(yaml_content)

        loader = FixtureLoader()
        fixtures = loader.load_file(str(fixture_file))

        assert len(fixtures) == 2
        assert fixtures[0].id == "commit_001"
        assert fixtures[1].id == "commit_002"

    def test_load_file_round_trip(self, tmp_path):
        """Test that loaded fixtures produce correct to_dict output."""
        yaml_content = (
            "id: rt_001\n"
            "description: Round-trip test\n"
            "setup:\n"
            "  - git init\n"
            "  - git add .\n"
            "prompt: 'Commit message for refactor'\n"
            "expected: 'refactor: simplify config loading'\n"
            "scoring:\n"
            "  type: similarity\n"
            "  threshold: 0.7\n"
        )

        fixture_file = tmp_path / "fixture.yaml"
        fixture_file.write_text(yaml_content)

        loader = FixtureLoader()
        fixtures = loader.load_file(str(fixture_file))

        assert len(fixtures) == 1
        d = fixtures[0].to_dict()
        assert d["id"] == "rt_001"
        assert d["scoring"]["threshold"] == 0.7
        assert Fixture.from_dict(d).id == "rt_001"

    def test_load_file_missing_required_field(self, tmp_path):
        """Test that a fixture missing a required field raises ValueError."""
        yaml_content = (
            "id: bad_001\n"
            "setup:\n"
            "  - git init\n"
            "prompt: Missing expected field\n"
        )

        fixture_file = tmp_path / "fixture.yaml"
        fixture_file.write_text(yaml_content)

        loader = FixtureLoader()
        with pytest.raises(ValueError, match="Missing required field"):
            loader.load_file(str(fixture_file))

    def test_load_file_missing_id(self, tmp_path):
        """Test that a fixture without an id field raises ValueError."""
        yaml_content = (
            "setup:\n"
            "  - git init\n"
            "prompt: No ID\n"
            "expected: some expected output\n"
        )

        fixture_file = tmp_path / "fixture.yaml"
        fixture_file.write_text(yaml_content)

        loader = FixtureLoader()
        with pytest.raises(ValueError, match="Missing required field"):
            loader.load_file(str(fixture_file))

    def test_load_file_invalid_yaml_not_dict(self, tmp_path):
        """Test that a fixture that is neither dict nor list raises ValueError."""
        yaml_content = "just a plain string"

        fixture_file = tmp_path / "fixture.yaml"
        fixture_file.write_text(yaml_content)

        loader = FixtureLoader()
        with pytest.raises(ValueError, match="Invalid fixture format"):
            loader.load_file(str(fixture_file))

    def test_load_file_setup_not_list(self, tmp_path):
        """Test that a fixture with non-list setup raises ValueError."""
        yaml_content = (
            "id: bad_setup\n"
            "setup: not a list\n"
            "prompt: test prompt\n"
            "expected: expected output\n"
        )

        fixture_file = tmp_path / "fixture.yaml"
        fixture_file.write_text(yaml_content)

        loader = FixtureLoader()
        with pytest.raises(ValueError, match="'setup' must be a list"):
            loader.load_file(str(fixture_file))

    def test_load_file_nonexistent(self):
        """Test that loading a non-existent file raises FileNotFoundError."""
        loader = FixtureLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_file("/no/such/path.yaml")

    def test_load_dir(self, tmp_path):
        """Test loading all .yaml files from a directory."""
        yaml1 = (
            "id: dir_001\n"
            "setup:\n"
            "  - git init\n"
            "prompt: test\n"
            "expected: expected\n"
        )
        yaml2 = (
            "id: dir_002\n"
            "setup:\n"
            "  - git init\n"
            "prompt: test2\n"
            "expected: expected2\n"
        )

        (tmp_path / "fix1.yaml").write_text(yaml1)
        (tmp_path / "fix2.yaml").write_text(yaml2)
        # Non-YAML file should be skipped
        (tmp_path / "readme.txt").write_text("This is not a fixture")
        (tmp_path / "data.yml").write_text(yaml2)

        loader = FixtureLoader()
        fixtures = loader.load_dir(str(tmp_path))

        ids = {f.id for f in fixtures}
        assert "dir_001" in ids
        assert "dir_002" in ids

    def test_load_dir_skips_non_yaml(self, tmp_path):
        """Test that load_dir skips non-.yaml files."""
        (tmp_path / "readme.txt").write_text("not a fixture")
        (tmp_path / "data.json").write_text('{"id": "bad"}')
        (tmp_path / "script.sh").write_text("#!/bin/bash")

        loader = FixtureLoader()
        fixtures = loader.load_dir(str(tmp_path))

        assert len(fixtures) == 0

    def test_load_dir_nonexistent(self):
        """Test that loading a non-existent directory raises FileNotFoundError."""
        loader = FixtureLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_dir("/no/such/dir")

    def test_load_file_empty(self, tmp_path):
        """Test that an empty YAML file returns an empty list."""
        fixture_file = tmp_path / "empty.yaml"
        fixture_file.write_text("")

        loader = FixtureLoader()
        fixtures = loader.load_file(str(fixture_file))

        assert fixtures == []
