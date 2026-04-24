"""Pytest configuration and fixtures for GitBench tests."""

import pytest

from gitbench.harness.model import MockModelClient
from gitbench.harness.types import Fixture, ModelMessage, Score


@pytest.fixture
def mock_model_client():
    """Create a MockModelClient instance with a default response."""
    return MockModelClient(response="Test response from mock model")


@pytest.fixture
def sample_fixture():
    """Create a sample Fixture for testing."""
    return Fixture(
        id="test_001",
        description="Test fixture for unit testing",
        setup=["git init", "git add ."],
        prompt="Generate a commit message for: Add new feature",
        expected="feat: add new feature",
        scoring={"type": "similarity", "threshold": 0.7},
    )


@pytest.fixture
def sample_message():
    """Create a sample ModelMessage for testing."""
    return ModelMessage(role="user", content="Hello, how are you?")


@pytest.fixture
def sample_score():
    """Create a sample Score for testing."""
    return Score(
        fixture_id="test_001",
        passed=True,
        similarity=0.85,
        model_output="feat: add new feature",
        error=None,
    )