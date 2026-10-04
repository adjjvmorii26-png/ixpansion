def test_deploy_status_does_not_expose_environment_presence():
    from api.deploy_status import handler

    result = handler({})
    assert "env" not in result
    assert "live_url" not in result
