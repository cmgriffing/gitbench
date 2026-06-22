"""Tests for judge configuration identity and hash invalidation.

These tests prove that every decision-relevant change to the judge
configuration invalidates the hash, while credentials and transient
capacity settings (timeout, retry count) do not affect the identity.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from gitbench.harness.judge import (
    JUDGE_AGGREGATION_METHOD,
    JUDGE_AGGREGATION_VERSION,
    JUDGE_RUBRIC_VERSION,
    build_judge_identity,
    compute_judge_config_hash,
)
from gitbench.harness.model import MockModelClient


def _mock_client(model: str = "judge-model", reasoning: str | None = None, base_url: str | None = None, adapter_name: str = "OpenAIAdapter"):
    """Create a mock model client with configurable attributes."""
    client = MagicMock()
    client.model = model
    client.reasoning_level = reasoning
    client._base_url = base_url
    client.base_url = base_url
    # Override class name for provider type detection.
    client.__class__ = type(adapter_name, (), {})
    return client


class TestIdentityStructure:
    """The canonical judge identity has the expected structure."""

    def test_identity_contains_members_rubric_and_aggregation(self):
        client = MockModelClient(model="judge-model")
        identity = build_judge_identity([client])
        assert "members" in identity
        assert "rubric_version" in identity
        assert "aggregation_method" in identity
        assert "aggregation_version" in identity

    def test_identity_member_includes_provider(self):
        client = MockModelClient(model="judge-model")
        identity = build_judge_identity([client])
        member = identity["members"][0]
        assert "provider" in member
        assert member["provider"] == "MockModelClient"

    def test_identity_is_secret_free(self):
        """No API keys or secrets appear in the identity."""
        client = MagicMock()
        client.model = "judge-model"
        client.reasoning_level = "high"
        client._base_url = "https://api.openai.com"
        client._api_key = "sk-secret-12345"
        client.base_url = "https://api.openai.com"
        identity = build_judge_identity([client])
        identity_json = repr(identity)
        assert "sk-secret-12345" not in identity_json
        assert "api_key" not in identity_json


class TestHashInvalidation:
    """Decision-relevant changes invalidate the hash."""

    def test_model_change_invalidates_hash(self):
        clients_a = [MockModelClient(model="judge-a")]
        clients_b = [MockModelClient(model="judge-b")]
        assert compute_judge_config_hash(clients_a) != compute_judge_config_hash(clients_b)

    def test_reasoning_level_change_invalidates_hash(self):
        clients_a = [MockModelClient(model="judge-model#low")]
        clients_b = [MockModelClient(model="judge-model#high")]
        assert compute_judge_config_hash(clients_a) != compute_judge_config_hash(clients_b)

    def test_base_url_change_invalidates_hash(self):
        client_a = MagicMock()
        client_a.model = "judge-model"
        client_a.reasoning_level = None
        client_a._base_url = "https://api.openai.com"
        client_a.base_url = "https://api.openai.com"
        client_a.__class__ = type("OpenAIAdapter", (), {})

        client_b = MagicMock()
        client_b.model = "judge-model"
        client_b.reasoning_level = None
        client_b._base_url = "https://api.other.com"
        client_b.base_url = "https://api.other.com"
        client_b.__class__ = type("OpenAIAdapter", (), {})

        assert compute_judge_config_hash([client_a]) != compute_judge_config_hash([client_b])

    def test_provider_change_invalidates_hash(self):
        """Changing the adapter/provider type invalidates the hash."""
        class FakeOpenAI:
            model = "judge-model"
            reasoning_level = None
            base_url = None
            _base_url = None

        class FakeOllama:
            model = "judge-model"
            reasoning_level = None
            base_url = None
            _base_url = None

        assert compute_judge_config_hash([FakeOpenAI()]) != compute_judge_config_hash([FakeOllama()])

    def test_member_order_matters(self):
        """Reordering judge members produces a different hash."""
        client_a = MockModelClient(model="judge-a")
        client_b = MockModelClient(model="judge-b")
        hash_1 = compute_judge_config_hash([client_a, client_b])
        hash_2 = compute_judge_config_hash([client_b, client_a])
        assert hash_1 != hash_2

    def test_member_count_change_invalidates_hash(self):
        """Adding or removing a member invalidates the hash."""
        client_a = MockModelClient(model="judge-a")
        client_b = MockModelClient(model="judge-b")
        hash_1 = compute_judge_config_hash([client_a])
        hash_2 = compute_judge_config_hash([client_a, client_b])
        assert hash_1 != hash_2

    def test_rubric_version_change_invalidates_hash(self):
        client = MockModelClient(model="judge-model")
        identity_a = build_judge_identity([client], rubric_version="v1")
        identity_b = build_judge_identity([client], rubric_version="v2")
        import hashlib, json
        hash_a = hashlib.sha256(json.dumps(identity_a, sort_keys=True).encode()).hexdigest()
        hash_b = hashlib.sha256(json.dumps(identity_b, sort_keys=True).encode()).hexdigest()
        assert hash_a != hash_b

    def test_aggregation_method_change_invalidates_hash(self):
        client = MockModelClient(model="judge-model")
        identity_a = build_judge_identity([client], aggregation_method="average")
        identity_b = build_judge_identity([client], aggregation_method="majority")
        import hashlib, json
        hash_a = hashlib.sha256(json.dumps(identity_a, sort_keys=True).encode()).hexdigest()
        hash_b = hashlib.sha256(json.dumps(identity_b, sort_keys=True).encode()).hexdigest()
        assert hash_a != hash_b

    def test_aggregation_version_change_invalidates_hash(self):
        client = MockModelClient(model="judge-model")
        identity_a = build_judge_identity([client], aggregation_version="v1")
        identity_b = build_judge_identity([client], aggregation_version="v2")
        import hashlib, json
        hash_a = hashlib.sha256(json.dumps(identity_a, sort_keys=True).encode()).hexdigest()
        hash_b = hashlib.sha256(json.dumps(identity_b, sort_keys=True).encode()).hexdigest()
        assert hash_a != hash_b


class TestTransientSettingsExcluded:
    """Credentials and transient capacity settings do not enter the identity."""

    def test_api_key_does_not_affect_hash(self):
        """Changing the API key does not change the hash."""
        class FakeAdapter:
            model = "judge-model"
            reasoning_level = None
            base_url = "https://api.openai.com"
            _base_url = "https://api.openai.com"

        client_a = FakeAdapter()
        client_a._api_key = "sk-key-a"
        client_b = FakeAdapter()
        client_b._api_key = "sk-key-b"

        assert compute_judge_config_hash([client_a]) == compute_judge_config_hash([client_b])

    def test_timeout_does_not_affect_hash(self):
        """Changing the timeout does not change the hash."""
        client_a = MockModelClient(model="judge-model", timeout=120)
        client_b = MockModelClient(model="judge-model", timeout=240)
        assert compute_judge_config_hash([client_a]) == compute_judge_config_hash([client_b])

    def test_retry_count_does_not_affect_hash(self):
        """Changing the retry count does not change the hash."""
        client_a = MockModelClient(model="judge-model", retry_count=3)
        client_b = MockModelClient(model="judge-model", retry_count=10)
        assert compute_judge_config_hash([client_a]) == compute_judge_config_hash([client_b])

    def test_attempt_gate_does_not_affect_hash(self):
        """The attempt gate (capacity coordination) does not enter the identity."""
        gate = MagicMock()
        client_a = MockModelClient(model="judge-model")
        client_b = MockModelClient(model="judge-model")
        # Simulate different attempt gates being attached.
        client_a._attempt_gate = gate
        client_b._attempt_gate = None
        assert compute_judge_config_hash([client_a]) == compute_judge_config_hash([client_b])

    def test_equivalent_clients_produce_same_hash(self):
        """Equivalent judge configurations produce the same hash."""
        clients_a = [MockModelClient(model="judge-1"), MockModelClient(model="judge-2")]
        clients_b = [MockModelClient(model="judge-1"), MockModelClient(model="judge-2")]
        assert compute_judge_config_hash(clients_a) == compute_judge_config_hash(clients_b)


class TestJudgeClientExposesHash:
    """JudgeClient exposes the config hash and identity."""

    def test_config_hash_property(self):
        client = MockModelClient(model="judge-model")
        from gitbench.harness.judge import JudgeClient
        judge = JudgeClient([client])
        assert judge.config_hash is not None
        assert isinstance(judge.config_hash, str)
        assert len(judge.config_hash) == 64  # SHA-256 hex

    def test_judge_identity_property(self):
        client = MockModelClient(model="judge-model")
        from gitbench.harness.judge import JudgeClient
        judge = JudgeClient([client])
        identity = judge.judge_identity
        assert "members" in identity
        assert "rubric_version" in identity
        assert identity["rubric_version"] == JUDGE_RUBRIC_VERSION
        assert identity["aggregation_method"] == JUDGE_AGGREGATION_METHOD
        assert identity["aggregation_version"] == JUDGE_AGGREGATION_VERSION