"""Regression tests for authentication at the API usage endpoint."""
import json
from types import SimpleNamespace

from api import auth


def _request(authorization=None):
    headers = {} if authorization is None else {"Authorization": authorization}
    return SimpleNamespace(path="/api/auth/usage", method="GET", headers=headers)


def _isolated_files(monkeypatch, tmp_path):
    keys_file = tmp_path / "api_keys.json"
    usage_file = tmp_path / "usage.json"
    keys_file.write_text("{}")
    usage_file.write_text("{}")
    monkeypatch.setattr(auth, "KEYS_FILE", keys_file)
    monkeypatch.setattr(auth, "USAGE_FILE", usage_file)
    return keys_file, usage_file


def test_usage_missing_authorization_rejected_without_mutation(monkeypatch, tmp_path):
    keys_file, usage_file = _isolated_files(monkeypatch, tmp_path)
    result = auth.handler(_request(), None)
    assert result == {"error": "authorization required"}
    assert json.loads(usage_file.read_text()) == {}
    assert json.loads(keys_file.read_text()) == {}


def test_usage_invalid_authorization_rejected_without_mutation(monkeypatch, tmp_path):
    keys_file, usage_file = _isolated_files(monkeypatch, tmp_path)
    initial = {"known": {"owner": "alice", "tier": "free", "active": False}}
    keys_file.write_text(json.dumps(initial))

    for authorization, expected in [
        ("Basic known", "invalid authorization scheme"),
        ("Bearer unknown", "key not found"),
        ("Bearer known", "key deactivated"),
        ("Bearer ", "authorization required"),
    ]:
        result = auth.handler(_request(authorization), None)
        assert result == {"error": expected}
        assert json.loads(usage_file.read_text()) == {}
        assert json.loads(keys_file.read_text()) == initial


def test_usage_valid_bearer_records_usage(monkeypatch, tmp_path):
    keys_file, usage_file = _isolated_files(monkeypatch, tmp_path)
    keys_file.write_text(json.dumps({
        "valid-key": {"owner": "alice", "tier": "pro", "active": True}
    }))
    result = auth.handler(_request("Bearer valid-key"), None)
    assert result["daily_calls"] == 1
    assert result["tier"] == "pro"
    assert result["over_limit"] is False
    usage = json.loads(usage_file.read_text())
    assert usage["valid-key"][auth.time.strftime("%Y-%m-%d")]["calls"] == 1
    assert usage["valid-key"][auth.time.strftime("%Y-%m-%d")]["endpoints"] == {
        "/api/auth/usage": 1
    }
