"""Contract tests for dashboard API read routes.

These routes are consumed by the browser dashboard and must resolve through
api/index.py without requiring a client-side credential.
"""


def test_dashboard_vibebot_state_route_is_callable():
    from api.index import _call

    result = _call("GET", "/api/vibebot/state")

    assert "error" not in result
    assert result["current_vibe"]
    assert "history" in result


def test_dashboard_emergent_skills_list_route_is_callable():
    from api.index import _call

    result = _call("GET", "/api/emergent_skills/list")

    assert "error" not in result
    assert isinstance(result, dict)
