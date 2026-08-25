from __future__ import annotations
"""Tests for Production Layer — docs, webhooks, usage dashboard."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_api_docs_endpoints():
    from api.docs import get_all_endpoints
    eps = get_all_endpoints()
    assert len(eps) > 30
    methods = set(ep["method"] for ep in eps)
    assert "GET" in methods
    assert "POST" in methods

def test_api_docs_openapi():
    from api.docs import get_openapi_spec
    spec = get_openapi_spec()
    assert spec["openapi"] == "3.0.0"
    assert "paths" in spec
    assert len(spec["paths"]) > 20

def test_api_docs_groups():
    from api.docs import get_all_endpoints
    eps = get_all_endpoints()
    groups = set(ep["group"] for ep in eps)
    assert "auth" in groups
    assert "crypto" in groups
    assert "marketplace" in groups

def test_api_docs_tiers():
    from api.docs import get_all_endpoints
    eps = get_all_endpoints()
    free = [e for e in eps if e["minimum_tier"] == "free"]
    pro = [e for e in eps if e["minimum_tier"] == "pro"]
    enterprise = [e for e in eps if e["minimum_tier"] == "enterprise"]
    assert len(free) > 10
    assert len(pro) > 0

def test_webhook_subscribe():
    from api.webhooks import WebhookSystem
    ws = WebhookSystem()
    result = ws.subscribe("https://test.com/hook", ["experiment.completed"])
    assert result["subscribed"]
    assert "webhook_id" in result

def test_webhook_trigger():
    from api.webhooks import WebhookSystem
    ws = WebhookSystem()
    ws.subscribe("https://test.com/hook2", ["payment.confirmed"])
    deliveries = ws.trigger("payment.confirmed", {"amount": 29})
    assert len(deliveries) >= 1

def test_webhook_list():
    from api.webhooks import WebhookSystem
    ws = WebhookSystem()
    hooks = ws.list_webhooks()
    assert isinstance(hooks, list)

def test_webhook_events():
    from api.webhooks import WebhookSystem
    ws = WebhookSystem()
    events = ws.event_types()
    assert "experiment.completed" in events
    assert "payment.confirmed" in events
    assert len(events) >= 8

def test_webhook_unsubscribe():
    from api.webhooks import WebhookSystem
    ws = WebhookSystem()
    r = ws.subscribe("https://test.com/unsub", ["milestone.reached"])
    result = ws.unsubscribe(r["webhook_id"])
    assert result["unsubscribed"]

def test_usage_dashboard_live():
    from api.usage_dashboard import get_live_metrics
    metrics = get_live_metrics()
    assert "api_calls_today" in metrics
    assert "total_experiments" in metrics
    assert metrics["total_experiments"] > 0

def test_usage_dashboard_history():
    from api.usage_dashboard import get_history
    history = get_history(3)
    assert len(history) == 3
    assert all("date" in h and "calls" in h for h in history)

def test_usage_dashboard_top():
    from api.usage_dashboard import get_top_users
    top = get_top_users(5)
    assert isinstance(top, list)

def test_landing_page_exists():
    from pathlib import Path
    index = Path("dashboard/index.html")
    assert index.exists()
    content = index.read_text()
    assert "IXpansion" in content
    assert "Scientist" in content
    assert "$29" in content

def test_premium_dashboard_exists():
    from pathlib import Path
    premium = Path("dashboard/premium.html")
    assert premium.exists()
    content = premium.read_text()
    assert "IXpansion" in content
