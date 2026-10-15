"""Deployment reality check — operational store, not env name alone."""


def test_deployment_reality_check_is_non_secret(monkeypatch):
    from api import auth
    import api.auth_store as auth_store
    from api.deploy_status import deployment_reality_check

    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.delenv("IXPANSION_AUTH_STORE", raising=False)
    monkeypatch.setattr(auth_store, "_ACTIVE_STORE", None)
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "SERVERLESS", True)
    result = deployment_reality_check()
    assert result["status"] == "blocked"
    assert result["store_operational"] is False
    blob = str(result).lower()
    assert "token" not in blob
    assert "secret" not in blob
    assert "password" not in blob


def test_deployment_reality_check_requires_operational_store(monkeypatch):
    from api import auth
    import api.auth_store as auth_store
    from api.deploy_status import deployment_reality_check

    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("IXPANSION_AUTH_STORE", "supabase")
    monkeypatch.setattr(auth_store, "_ACTIVE_STORE", None)
    monkeypatch.setattr(auth, "SERVERLESS", True)
    monkeypatch.setattr(auth_store, "SERVERLESS", True)
    result = deployment_reality_check()
    assert result["status"] == "blocked"
    assert result["named_backend"] == "supabase"

    mem = auth.MemoryAuthStore()
    auth.register_auth_store(mem)
    result2 = deployment_reality_check()
    assert result2["status"] == "ready"
    assert result2["store_operational"] is True
    assert result2["auth_persistence"] == "durable"
    assert result2["store"] == "memory"
