"""Benchmark base classes for GitBench."""

from abc import ABC, abstractmethod

from gitbench.harness.types import Fixture, Score

from gitbench.benchmarks.stash_recovery import Benchmark, StashRecoveryBenchmark
from gitbench.benchmarks.commit_squash import CommitSquashBenchmark

__all__ = ["Benchmark", "StashRecoveryBenchmark", "CommitSquashBenchmark"]
