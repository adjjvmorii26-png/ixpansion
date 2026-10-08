def test_deployment_reality_check_is_non_secret(monkeypatch):
    from api.deploy_status import deployment_reality_check

    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.delenv("IXPANSION_AUTH_STORE", raising=False)
    result = deployment_reality_check()
    assert result["status"] == "blocked"
    assert "token" not in str(result).lower()
    assert "secret" not in str(result).lower()


def test_deployment_reality_check_accepts_durable_backend(monkeypatch):
    from api.deploy_status import deployment_reality_check

    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("IXPANSION_AUTH_STORE", "supabase")
    result = deployment_reality_check()
    assert result["status"] == "ready"
    assert result["auth_persistence"] == "durable"
