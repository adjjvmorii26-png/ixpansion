import pytest


def test_local_auth_storage_remains_available(monkeypatch, tmp_path):
    import api.auth as auth
    monkeypatch.setattr(auth, "SERVERLESS", False)
    monkeypatch.setattr(auth, "KEYS_FILE", tmp_path / "api_keys.json")
    monkeypatch.setattr(auth, "USAGE_FILE", tmp_path / "usage.json")
    result = auth.generate_api_key("contract-test", "free")
    assert result["api_key"].startswith("ixp_")


def test_serverless_auth_storage_fails_closed_without_durable_backend(monkeypatch):
    import api.auth as auth
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth, "PERSISTENCE_BACKEND", "")
    with pytest.raises(RuntimeError, match="auth persistence is not configured"):
        auth._assert_persistence_contract()


def test_serverless_auth_storage_accepts_named_backend(monkeypatch):
    import api.auth as auth
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth, "PERSISTENCE_BACKEND", "supabase")
    auth._assert_persistence_contract()
