"""Tests for GitBench model interface."""

from unittest.mock import MagicMock, patch

import pytest

from gitbench.harness.model import MockModelClient, ModelInterface, OpenAIAdapter
from gitbench.harness.types import ModelMessage

# Try to import openai for conditional tests
openai = pytest.importorskip("openai")


class TestModelInterface:
    """Tests for ModelInterface ABC."""

    def test_is_abstract(self):
        """Test that ModelInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ModelInterface()


class TestMockModelClient:
    """Tests for MockModelClient."""

    def test_creation(self):
        """Test creating a MockModelClient."""
        client = MockModelClient(response="Test response")
        assert client.response == "Test response"

    def test_default_response(self):
        """Test default response value."""
        client = MockModelClient()
        assert client.response == "Mock response"

    def test_generate_returns_configured_response(self):
        """Test that generate returns the configured response."""
        client = MockModelClient(response="Expected output")
        messages = [ModelMessage(role="user", content="Hello")]
        result = client.generate(messages)
        assert result == "Expected output"

    def test_generate_stores_messages(self):
        """Test that generate stores the messages for inspection."""
        client = MockModelClient(response="Output")
        messages = [
            ModelMessage(role="system", content="You are helpful"),
            ModelMessage(role="user", content="Hi"),
        ]
        client.generate(messages)
        assert client.last_messages == messages

    def test_generate_tracks_call_count(self):
        """Test that generate increments call count."""
        client = MockModelClient(response="Response")
        messages = [ModelMessage(role="user", content="Test")]
        assert client.call_count == 0
        client.generate(messages)
        assert client.call_count == 1
        client.generate(messages)
        assert client.call_count == 2

    def test_set_response(self):
        """Test updating the mock response."""
        client = MockModelClient(response="Original")
        messages = [ModelMessage(role="user", content="Test")]
        assert client.generate(messages) == "Original"

        client.set_response("Updated")
        assert client.generate(messages) == "Updated"

    def test_generate_accepts_kwargs(self):
        """Test that generate accepts additional kwargs without error."""
        client = MockModelClient(response="Output")
        messages = [ModelMessage(role="user", content="Test")]
        # Should not raise, kwargs are ignored
        result = client.generate(messages, temperature=0.5, max_tokens=100)
        assert result == "Output"


class TestOpenAIAdapter:
    """Tests for OpenAIAdapter."""

    def test_creation(self):
        """Test creating an OpenAIAdapter."""
        adapter = OpenAIAdapter(model="gpt-4o-mini")
        assert adapter.model == "gpt-4o-mini"

    def test_creation_with_custom_api_key(self):
        """Test creating with custom API key."""
        adapter = OpenAIAdapter(model="gpt-4", api_key="sk-test-key")
        assert adapter._api_key == "sk-test-key"

    def test_default_model(self):
        """Test that default model is set correctly."""
        adapter = OpenAIAdapter()
        assert adapter.model == "gpt-4o-mini"

    @patch("openai.OpenAI")
    def test_generate_calls_openai_api(self, mock_openai_class):
        """Test that generate calls the OpenAI API correctly."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Generated output"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        adapter = OpenAIAdapter(api_key="test-key")
        adapter._client = mock_client

        messages = [
            ModelMessage(role="system", content="You are helpful"),
            ModelMessage(role="user", content="Generate a commit message"),
        ]
        result = adapter.generate(messages)

        assert result == "Generated output"
        mock_client.chat.completions.create.assert_called_once()

        # Verify the call format
        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == "gpt-4o-mini"
        assert len(call_kwargs.kwargs["messages"]) == 2

    @patch("openai.OpenAI")
    def test_generate_passes_extra_kwargs(self, mock_openai_class):
        """Test that generate passes extra kwargs to the API."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Output"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        adapter = OpenAIAdapter(api_key="test-key")
        adapter._client = mock_client

        messages = [ModelMessage(role="user", content="Test")]
        adapter.generate(messages, temperature=0.7, max_tokens=50)

        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["temperature"] == 0.7
        assert call_kwargs.kwargs["max_tokens"] == 50

    def test_client_lazy_loads_openai(self):
        """Test that the client property lazy-loads the OpenAI module."""
        adapter = OpenAIAdapter(api_key="test-key")

        # Client should be None until accessed
        assert adapter._client is None

        # Access the client property - should raise ImportError if openai not installed
        with pytest.raises(ImportError):
            _ = adapter.client

    @patch("openai.OpenAI")
    def test_empty_response_handling(self, mock_openai_class):
        """Test handling of empty response content."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = ""
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        adapter = OpenAIAdapter(api_key="test-key")
        adapter._client = mock_client

        messages = [ModelMessage(role="user", content="Test")]
        result = adapter.generate(messages)
        assert result == ""