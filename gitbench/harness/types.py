"""Core types for the GitBench harness."""

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class ModelMessage:
    """A message in a model conversation."""

    role: str
    content: str

    def to_dict(self) -> dict:
        """Convert to dictionary format expected by model APIs."""
        return {"role": self.role, "content": self.content}

    @classmethod
    def from_dict(cls, data: dict) -> "ModelMessage":
        """Create from dictionary."""
        return cls(role=data["role"], content=data["content"])


@dataclass
class Fixture:
    """A test fixture for benchmarking."""

    id: str
    description: str
    setup: list[str]  # List of git commands to run as setup
    prompt: str
    expected: str
    scoring: dict[str, Any]  # Contains 'type' and 'threshold'

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Fixture":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Score:
    """A scoring result for a single fixture."""

    fixture_id: str
    passed: bool
    similarity: float
    model_output: str
    error: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Score":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class BenchmarkResult:
    """The result of running a benchmark."""

    benchmark: str
    total: int
    passed: int
    pass_at_k: float
    scores: list[Score]
    errors: int

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "benchmark": self.benchmark,
            "total": self.total,
            "passed": self.passed,
            "pass_at_k": self.pass_at_k,
            "scores": [s.to_dict() for s in self.scores],
            "errors": self.errors,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BenchmarkResult":
        """Create from dictionary."""
        scores = [Score.from_dict(s) for s in data["scores"]]
        return cls(
            benchmark=data["benchmark"],
            total=data["total"],
            passed=data["passed"],
            pass_at_k=data["pass_at_k"],
            scores=scores,
            errors=data["errors"],
        )