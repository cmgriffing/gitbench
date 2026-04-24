"""Model interface for GitBench."""

from abc import ABC, abstractmethod
from typing import Any

from .types import ModelMessage


class ModelInterface(ABC):
    """Abstract base class for model adapters."""

    @abstractmethod
    def generate(self, messages: list[ModelMessage], **kwargs: Any) -> str:
        """Generate a response from the model.

        Args:
            messages: List of ModelMessage objects representing the conversation.
            **kwargs: Additional model-specific parameters.

        Returns:
            The model's response as a string.

        Raises:
            Exception: If the model call fails.
        """
        ...


class OpenAIAdapter(ModelInterface):
    """Adapter for OpenAI API compatible models."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None, timeout: int = 30, retry_count: int = 3):
        """Initialize the OpenAI adapter.

        Args:
            model: The model identifier (default: gpt-4o-mini).
            api_key: Optional API key. If not provided, reads from OPENAI_API_KEY env var.
            timeout: Timeout in seconds for model generation (default: 30).
            retry_count: Number of retries on failure (default: 3).
        """
        self.model = model
        self.timeout = timeout
        self.retry_count = retry_count
        self._api_key = api_key
        self._client = None

    @property
    def client(self):
        """Lazy-load the OpenAI client."""
        if self._client is None:
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "openai package not installed. Install with: pip install openai"
                )
            api_key = self._api_key or openai.api_key
            if not api_key:
                raise ValueError(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                    "or pass api_key parameter."
                )
            self._client = openai.OpenAI(api_key=api_key)
        return self._client

    def generate(self, messages: list[ModelMessage], **kwargs: Any) -> str:
        """Generate a response using the OpenAI API.

        Args:
            messages: List of ModelMessage objects.
            **kwargs: Additional parameters (temperature, max_tokens, etc.).

        Returns:
            The model's response text.
        """
        model_messages = [msg.to_dict() for msg in messages]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=model_messages,
            **kwargs,
        )

        return response.choices[0].message.content or ""


class MockModelClient(ModelInterface):
    """Mock model client for testing."""

    def __init__(self, response: str = "Mock response"):
        """Initialize with a fixed response.

        Args:
            response: The fixed string to return on every call.
        """
        self.response = response
        self.call_count = 0
        self.last_messages = None

    def generate(self, messages: list[ModelMessage], **kwargs: Any) -> str:
        """Return the configured mock response.

        Args:
            messages: List of ModelMessage objects (stored for inspection).
            **kwargs: Additional parameters (ignored).

        Returns:
            The configured mock response string.
        """
        self.call_count += 1
        self.last_messages = messages
        return self.response

    def set_response(self, response: str) -> None:
        """Update the mock response.

        Args:
            response: New response string to return.
        """
        self.response = response