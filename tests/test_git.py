"""Tests for the Git executor."""

import os
import uuid
from pathlib import Path

import pytest

from gitbench.utils.git import GitExecutor


class TestGitExecutor:
    """Tests for GitExecutor class."""

    def test_init_raises_when_git_not_found(self, monkeypatch):
        """Test that GitExecutor raises RuntimeError when git is not found."""
        import os

        monkeypatch.setenv("PATH", "/nonexistent/bin")
        original_which = __import__("shutil").which

        def fake_which(cmd):
            if cmd == "git":
                return None
            return original_which(cmd)

        monkeypatch.setattr("shutil.which", fake_which)

        with pytest.raises(RuntimeError, match="git command not found"):
            GitExecutor()

    def test_setup_repo_creates_directory(self, tmp_path):
        """Test that setup_repo creates the repository directory."""
        executor = GitExecutor(base_dir=str(tmp_path))
        repo_name = f"test_repo_{uuid.uuid4().hex[:8]}"

        repo_path = executor.setup_repo(repo_name, [])

        assert Path(repo_path).exists()
        assert Path(repo_path).is_dir()

    def test_setup_repo_runs_git_init(self, tmp_path):
        """Test that setup_repo runs git init and creates a valid git repo."""
        executor = GitExecutor(base_dir=str(tmp_path))
        repo_name = f"test_git_init_{uuid.uuid4().hex[:8]}"

        repo_path = executor.setup_repo(repo_name, ["git init"])
        git_dir = Path(repo_path) / ".git"

        assert git_dir.exists()
        assert git_dir.is_dir()

    def test_setup_repo_runs_custom_commands(self, tmp_path):
        """Test that setup_repo runs custom setup commands."""
        executor = GitExecutor(base_dir=str(tmp_path))
        repo_name = f"test_custom_{uuid.uuid4().hex[:8]}"

        commands = [
            "git init",
            'echo "hello world" > file.txt',
            "git add .",
            'git commit -m "initial commit"',
        ]

        repo_path = executor.setup_repo(repo_name, commands)

        # Verify file was created
        assert (Path(repo_path) / "file.txt").read_text().strip() == "hello world"
        # Verify git commit was recorded
        result = os.system(f"git -C {repo_path} log --oneline | grep 'initial commit' > /dev/null")
        assert result == 0

    def test_cleanup_removes_tree(self, tmp_path):
        """Test that cleanup removes the repository directory."""
        executor = GitExecutor(base_dir=str(tmp_path))
        repo_name = f"test_cleanup_{uuid.uuid4().hex[:8]}"

        repo_path = executor.setup_repo(repo_name, ["git init"])
        assert Path(repo_path).exists()

        executor.cleanup()
        assert not Path(repo_path).exists()

    def test_cleanup_idempotent(self, tmp_path):
        """Test that calling cleanup twice does not raise an error."""
        executor = GitExecutor(base_dir=str(tmp_path))
        repo_name = f"test_idempotent_{uuid.uuid4().hex[:8]}"

        repo_path = executor.setup_repo(repo_name, ["git init"])
        executor.cleanup()
        executor.cleanup()  # Should not raise

    def test_same_repo_name_uses_isolated_workspaces(self, tmp_path):
        """Test that same-named repos do not share sibling temp paths."""
        repo_name = "same_fixture_name"
        first = GitExecutor(base_dir=str(tmp_path))
        second = GitExecutor(base_dir=str(tmp_path))

        first_path = first.setup_repo(repo_name, ['echo "first" > ../sibling.txt'])
        second_path = second.setup_repo(repo_name, ['echo "second" > ../sibling.txt'])

        first_parent = Path(first_path).parent
        second_parent = Path(second_path).parent
        assert first_parent != second_parent
        assert (first_parent / "sibling.txt").read_text().strip() == "first"
        assert (second_parent / "sibling.txt").read_text().strip() == "second"

        first.cleanup()
        second.cleanup()
        assert not first_parent.exists()
        assert not second_parent.exists()

    def test_setup_repo_command_failure(self, tmp_path, capsys):
        """Test that a failing command raises RuntimeError."""
        executor = GitExecutor(base_dir=str(tmp_path))
        repo_name = f"test_fail_{uuid.uuid4().hex[:8]}"

        with pytest.raises(RuntimeError, match="Command failed"):
            executor.setup_repo(repo_name, ["git init", "nonexistent_command_xyz"])

    def test_repo_path_property(self, tmp_path):
        """Test that repo_path property returns None before setup and path after."""
        executor = GitExecutor(base_dir=str(tmp_path))

        assert executor.repo_path is None

        repo_name = f"test_prop_{uuid.uuid4().hex[:8]}"
        repo_path = executor.setup_repo(repo_name, [])

        assert executor.repo_path == repo_path

        executor.cleanup()
        assert executor.repo_path is None
