"""Auth persistence contract — durable adapter required in serverless."""
import pytest

from api.auth_store import AuthStore


def _reset_auth(monkeypatch):
    import api.auth as auth
    import api.auth_store as auth_store
    monkeypatch.setattr(auth_store, "_ACTIVE_STORE", None)
    monkeypatch.setattr(auth, "SERVERLESS", False)
    monkeypatch.setattr(auth_store, "SERVERLESS", False)
    return auth


class ContractDurableStore(AuthStore):
    """Test double for the adapter contract; not a real persistence backend."""

    name = "contract_durable_test"
    durable = True

    def __init__(self):
        self._keys = {}
        self._usage = {}
        self.writes = 0

    def ensure(self):
        pass

    def load_keys(self):
        return dict(self._keys)

    def save_keys(self, keys):
        self._keys = dict(keys)
        self.writes += 1

    def load_usage(self):
        return dict(self._usage)

    def save_usage(self, usage):
        self._usage = dict(usage)
        self.writes += 1

    def health(self):
        return {"ok": True, "name": self.name, "durable": True}


def test_local_auth_storage_uses_local_json_store(monkeypatch, tmp_path):
    auth = _reset_auth(monkeypatch)
    store = auth.LocalJsonAuthStore(tmp_path / "api_keys.json", tmp_path / "usage.json")
    auth.register_auth_store(store)
    result = auth.generate_api_key("contract-test", "free")
    assert result["api_key"].startswith("ixp_")
    assert result["api_key"] in store.load_keys()


def test_serverless_fails_closed_without_adapter(monkeypatch):
    auth = _reset_auth(monkeypatch)
    import api.auth_store as auth_store
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "PERSISTENCE_BACKEND", "")
    with pytest.raises(RuntimeError, match="auth persistence"):
        auth._assert_persistence_contract()


def test_serverless_named_backend_without_adapter_still_fails(monkeypatch):
    """An environment name alone is not proof of operational storage."""
    auth = _reset_auth(monkeypatch)
    import api.auth_store as auth_store
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "PERSISTENCE_BACKEND", "supabase")
    with pytest.raises(RuntimeError, match="auth persistence"):
        auth._assert_persistence_contract()


def test_memory_store_is_not_a_serverless_durable_adapter(monkeypatch):
    """MemoryAuthStore is test-only and must never satisfy production durability."""
    auth = _reset_auth(monkeypatch)
    import api.auth_store as auth_store
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "PERSISTENCE_BACKEND", "external")
    auth.register_auth_store(auth.MemoryAuthStore())
    with pytest.raises(RuntimeError, match="durable"):
        auth._assert_persistence_contract()


def test_serverless_accepts_healthy_registered_durable_contract(monkeypatch):
    """Contract test only; this fake is not evidence of real backend durability."""
    auth = _reset_auth(monkeypatch)
    import api.auth_store as auth_store
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "PERSISTENCE_BACKEND", "external")
    store = ContractDurableStore()
    auth.register_auth_store(store)
    auth._assert_persistence_contract()


def test_generate_api_key_writes_through_registered_store(monkeypatch):
    auth = _reset_auth(monkeypatch)
    store = auth.MemoryAuthStore()
    auth.register_auth_store(store)
    result = auth.generate_api_key("write-through-proof", "pro")
    key = result["api_key"]
    assert store.writes >= 1
    assert key in store.load_keys()


def test_store_write_failure_surfaces_to_caller(monkeypatch):
    auth = _reset_auth(monkeypatch)

    class FailingStore(auth.MemoryAuthStore):
        def save_keys(self, keys):
            raise OSError("simulated storage outage")

    auth.register_auth_store(FailingStore())
    with pytest.raises(OSError, match="simulated storage outage"):
        auth.generate_api_key("failure-proof", "free")


def test_sequential_store_writes_are_visible_to_subsequent_reads(monkeypatch):
    auth = _reset_auth(monkeypatch)
    store = auth.MemoryAuthStore()
    auth.register_auth_store(store)
    auth._save_keys({"first": {"active": True}})
    auth._save_keys({"second": {"active": True}})
    assert store.load_keys() == {"second": {"active": True}}


def test_serverless_rejects_unhealthy_durable_adapter(monkeypatch):
    auth = _reset_auth(monkeypatch)
    import api.auth_store as auth_store
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "PERSISTENCE_BACKEND", "external")

    class UnhealthyStore(ContractDurableStore):
        def health(self):
            return {"ok": False, "name": self.name, "durable": True}

    auth.register_auth_store(UnhealthyStore())
    with pytest.raises(RuntimeError, match="health"):
        auth._assert_persistence_contract()


def test_get_auth_store_fails_closed_on_serverless(monkeypatch):
    auth = _reset_auth(monkeypatch)
    import api.auth_store as auth_store
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "SERVERLESS", True)
    with pytest.raises(RuntimeError, match="auth persistence"):
        auth.get_auth_store()
