from __future__ import annotations
"""Tests for Revenue Infrastructure — auth, marketplace, billing, analytics."""
import sys
import os
import tempfile
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_api_key_generation():
    from api.auth import generate_api_key, validate_key
    result = generate_api_key("test_user", "pro")
    assert result["api_key"].startswith("ixp_")
    assert result["tier"] == "pro"
    validation = validate_key(result["api_key"])
    assert validation["valid"]
    assert validation["tier"] == "pro"

def test_api_key_validation():
    from api.auth import validate_key
    result = validate_key("ixp_nonexistent")
    assert not result["valid"]

def test_usage_tracking():
    from api.auth import generate_api_key, record_usage
    result = generate_api_key("usage_test", "free")
    key = result["api_key"]
    usage = record_usage(key, "/api/experiments")
    assert usage["daily_calls"] == 1
    assert usage["daily_limit"] == 100
    usage2 = record_usage(key, "/api/health")
    assert usage2["daily_calls"] == 2

def test_experiment_access():
    from api.auth import generate_api_key, check_experiment_access
    result = generate_api_key("access_test", "free")
    key = result["api_key"]
    access = check_experiment_access(key, "photon_memory")
    assert access["allowed"]

def test_marketplace_publish():
    from api.marketplace import publish_experiment, list_experiments
    result = publish_experiment(
        "test_exp", "creator1", "A test experiment",
        "quantum", 9.99, tags=["test"]
    )
    assert result["published"]
    listing = list_experiments()
    assert listing["total"] >= 1

def test_marketplace_purchase():
    from api.marketplace import publish_experiment, purchase_experiment
    result = publish_experiment(
        "buyable_exp", "seller", "Buy this", "ecology", 5.00
    )
    purchase = purchase_experiment(result["id"], "buyer1")
    assert purchase["purchased"]
    assert purchase["price"] == 5.00
    assert purchase["commission"] == 1.00

def test_marketplace_earnings():
    from api.marketplace import publish_experiment, purchase_experiment, get_earnings
    result = publish_experiment("earn_exp", "earner", "Earn money", "folklore", 10.00)
    purchase_experiment(result["id"], "buyer2")
    purchase_experiment(result["id"], "buyer3")
    earnings = get_earnings("earner")
    assert earnings["total"] >= 16.00
    assert len(earnings["transactions"]) >= 2

def test_billing_subscribe():
    from api.billing import subscribe, get_status
    result = subscribe("user1", "pro", "monthly")
    assert result["subscribed"]
    assert result["price"] == 29
    status = get_status("user1")
    assert status["active"]
    assert status["plan"] == "pro"

def test_billing_cancel():
    from api.billing import subscribe, cancel, get_status
    subscribe("cancel_user", "pro")
    cancel("cancel_user")
    status = get_status("cancel_user")
    assert not status["active"]

def test_billing_invoice():
    from api.billing import subscribe, generate_invoice, get_invoices
    subscribe("inv_user", "enterprise", "yearly")
    invoice = generate_invoice("inv_user")
    assert "invoice" in invoice
    assert invoice["invoice"]["amount"] == 1990
    invoices = get_invoices("inv_user")
    assert len(invoices["invoices"]) >= 1

def test_analytics_overview():
    from api.analytics import get_overview
    overview = get_overview()
    assert "total_experiments" in overview
    assert overview["total_experiments"] > 0
    assert "system_health" in overview

def test_analytics_experiment_metrics():
    from api.analytics import get_experiment_metrics
    metrics = get_experiment_metrics()
    assert len(metrics) > 0
    assert "name" in metrics[0]
    assert "lines" in metrics[0]

def test_analytics_performance():
    from api.analytics import get_performance_data
    perf = get_performance_data()
    assert perf["experiment_files"] > 0
    assert perf["experiment_lines"] > 0

def test_tier_limits():
    from api.auth import TIERS
    assert TIERS["free"]["daily_limit"] == 100
    assert TIERS["pro"]["daily_limit"] == 10_000
    assert TIERS["enterprise"]["daily_limit"] == -1
    assert TIERS["free"]["monthly_price_usd"] == 0
    assert TIERS["pro"]["monthly_price_usd"] == 0  # all FREE

def test_marketplace_filtering():
    from api.marketplace import publish_experiment, list_experiments
    publish_experiment("q_exp", "c", "desc", "quantum", 1.00)
    publish_experiment("e_exp", "c", "desc", "ecology", 2.00)
    quantum = list_experiments(category="quantum")
    assert all(e["category"] == "quantum" for e in quantum["experiments"])
    ecology = list_experiments(category="ecology")
    assert all(e["category"] == "ecology" for e in ecology["experiments"])
