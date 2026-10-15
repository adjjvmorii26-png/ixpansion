"""Auth persistence contract — real adapter or fail closed."""
import pytest


def _reset_auth(monkeypatch):
    import api.auth as auth
    import api.auth_store as auth_store
    monkeypatch.setattr(auth_store, "_ACTIVE_STORE", None)
    monkeypatch.setattr(auth, "SERVERLESS", False)
    monkeypatch.setattr(auth_store, "SERVERLESS", False)
    return auth


def test_local_auth_storage_uses_local_json_store(monkeypatch, tmp_path):
    auth = _reset_auth(monkeypatch)
    store = auth.LocalJsonAuthStore(tmp_path / "api_keys.json", tmp_path / "usage.json")
    auth.register_auth_store(store)
    result = auth.generate_api_key("contract-test", "free")
    assert result["api_key"].startswith("ixp_")
    keys = store.load_keys()
    assert result["api_key"] in keys


def test_serverless_fails_closed_without_adapter(monkeypatch):
    auth = _reset_auth(monkeypatch)
    import api.auth_store as auth_store
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "PERSISTENCE_BACKEND", "")
    with pytest.raises(RuntimeError, match="auth persistence is not configured"):
        auth._assert_persistence_contract()


def test_serverless_named_backend_without_adapter_still_fails(monkeypatch):
    """Env name alone is not proof of operational storage."""
    auth = _reset_auth(monkeypatch)
    import api.auth_store as auth_store
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "PERSISTENCE_BACKEND", "supabase")
    with pytest.raises(RuntimeError, match="auth persistence is not configured"):
        auth._assert_persistence_contract()


def test_serverless_accepts_registered_durable_adapter(monkeypatch):
    auth = _reset_auth(monkeypatch)
    import api.auth_store as auth_store
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "PERSISTENCE_BACKEND", "external")
    mem = auth.MemoryAuthStore()
    auth.register_auth_store(mem)
    auth._assert_persistence_contract()
    result = auth.generate_api_key("durable-proof", "pro")
    assert result["api_key"].startswith("ixp_")
    assert mem.writes >= 1
    assert result["api_key"] in mem.load_keys()


def test_get_auth_store_fail_closed_on_serverless(monkeypatch):
    auth = _reset_auth(monkeypatch)
    import api.auth_store as auth_store
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "SERVERLESS", True)
    with pytest.raises(RuntimeError, match="auth persistence"):
        auth.get_auth_store()
