"""Billing & Subscription Management — handles tier subscriptions and invoicing.

Integrates with the auth system to manage subscriptions, generate invoices,
and handle upgrades/downgrades.

Usage:
    GET  /api/billing/plans       — list subscription plans
    POST /api/billing/subscribe   — subscribe to a plan
    GET  /api/billing/invoice     — generate invoice
    POST /api/billing/cancel      — cancel subscription
    GET  /api/billing/status      — subscription status
"""
from __future__ import annotations

import hashlib
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SUBSCRIPTIONS_FILE = ROOT / ".runtime" / "subscriptions.json"
INVOICES_FILE = ROOT / ".runtime" / "invoices.json"

PLANS = {
    "free": {
        "id": "free",
        "name": "Explorer",
        "price_monthly": 0,
        "price_yearly": 0,
        "daily_api_calls": 100,
        "experiments": "basic (12 modules)",
        "dashboard": "basic",
        "support": "community",
        "features": [
            "12 curated experiments",
            "Basic dashboard",
            "Community support",
            "100 API calls/day",
        ],
    },
    "pro": {
        "id": "pro",
        "name": "Scientist",
        "price_monthly": 29,
        "price_yearly": 290,
        "daily_api_calls": 10_000,
        "experiments": "all (157+ modules)",
        "dashboard": "advanced with real-time",
        "support": "email 48h",
        "features": [
            "157+ experiments",
            "Advanced dashboard",
            "Real-time monitoring",
            "10,000 API calls/day",
            "Priority execution",
            "Anomaly detection",
            "Constellation mapping",
            "Email support",
        ],
    },
    "enterprise": {
        "id": "enterprise",
        "name": "Architect",
        "price_monthly": 199,
        "price_yearly": 1990,
        "daily_api_calls": -1,
        "experiments": "all + custom agents",
        "dashboard": "full + custom views",
        "support": "dedicated Slack",
        "features": [
            "Everything in Scientist",
            "Unlimited API calls",
            "Custom agent development",
            "Custom integrations",
            "Dedicated Slack channel",
            "99.9% SLA",
            "Webhook notifications",
            "Bulk operations",
            "White-label options",
            "Priority support < 1h",
        ],
    },
}


def _ensure_files():
    SUBSCRIPTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not SUBSCRIPTIONS_FILE.exists():
        SUBSCRIPTIONS_FILE.write_text("{}")
    if not INVOICES_FILE.exists():
        INVOICES_FILE.write_text("{}")


def _load_subs() -> Dict:
    _ensure_files()
    return json.loads(SUBSCRIPTIONS_FILE.read_text())


def _save_subs(subs: Dict):
    _ensure_files()
    SUBSCRIPTIONS_FILE.write_text(json.dumps(subs, indent=2))


def _load_invoices() -> Dict:
    _ensure_files()
    return json.loads(INVOICES_FILE.read_text())


def _save_invoices(invoices: Dict):
    _ensure_files()
    INVOICES_FILE.write_text(json.dumps(invoices, indent=2))


def subscribe(owner: str, plan_id: str, billing_period: str = "monthly") -> Dict:
    if plan_id not in PLANS:
        return {"error": f"unknown plan: {plan_id}"}
    plan = PLANS[plan_id]
    if billing_period == "yearly":
        price = plan["price_yearly"]
    else:
        price = plan["price_monthly"]

    invoice_id = hashlib.sha256(f"{owner}:{plan_id}:{time.time()}".encode()).hexdigest()[:12]

    subs = _load_subs()
    subs[owner] = {
        "plan": plan_id,
        "billing_period": billing_period,
        "price": price,
        "subscribed_at": time.time(),
        "active": True,
    }
    _save_subs(subs)

    invoices = _load_invoices()
    if owner not in invoices:
        invoices[owner] = []
    invoices[owner].append({
        "id": invoice_id,
        "plan": plan_id,
        "amount": price,
        "period": billing_period,
        "status": "paid",
        "created": time.time(),
    })
    _save_invoices(invoices)

    return {
        "subscribed": True,
        "plan": plan["name"],
        "price": price,
        "period": billing_period,
        "invoice_id": invoice_id,
    }


def get_status(owner: str) -> Dict:
    subs = _load_subs()
    if owner not in subs:
        return {"active": False, "plan": "free", "message": "no subscription"}
    sub = subs[owner]
    plan = PLANS.get(sub["plan"], PLANS["free"])
    return {
        "active": sub["active"],
        "plan": sub["plan"],
        "plan_name": plan["name"],
        "price": sub["price"],
        "period": sub["billing_period"],
        "subscribed_at": sub["subscribed_at"],
        "features": plan["features"],
    }


def cancel(owner: str) -> Dict:
    subs = _load_subs()
    if owner not in subs:
        return {"error": "no active subscription"}
    subs[owner]["active"] = False
    _save_subs(subs)
    return {"cancelled": True, "owner": owner}


def get_invoices(owner: str) -> Dict:
    invoices = _load_invoices()
    return {"invoices": invoices.get(owner, [])}


def generate_invoice(owner: str) -> Dict:
    status = get_status(owner)
    if not status["active"]:
        return {"error": "no active subscription"}
    invoices = _load_invoices()
    existing = invoices.get(owner, [])
    invoice_id = hashlib.sha256(f"{owner}:{time.time()}".encode()).hexdigest()[:12]
    invoice = {
        "id": invoice_id,
        "owner": owner,
        "plan": status["plan"],
        "amount": status["price"],
        "period": status["period"],
        "status": "pending",
        "created": time.time(),
    }
    if owner not in invoices:
        invoices[owner] = []
    invoices[owner].append(invoice)
    _save_invoices(invoices)
    return {"invoice": invoice}


def handler(request, response):
    """API handler for billing endpoints."""
    return {"plans": PLANS}


def demo():
    print("=== Billing & Subscription System ===")
    print("\nPlans:")
    for pid, plan in PLANS.items():
        print(f"  {plan['name']} ({pid}): ${plan['price_monthly']}/mo "
              f"| ${plan['price_yearly']}/yr")
        for feat in plan["features"][:3]:
            print(f"    - {feat}")
        if len(plan["features"]) > 3:
            print(f"    ... +{len(plan['features'])-3} more")

    result = subscribe("user_aleph", "pro", "monthly")
    print(f"\nSubscription: {result}")

    status = get_status("user_aleph")
    print(f"Status: plan={status['plan_name']}, active={status['active']}")

    invoice = generate_invoice("user_aleph")
    print(f"Invoice: {invoice}")

    return {"plans": PLANS, "status": status}


if __name__ == "__main__":
    demo()

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "0", "module": "billing"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
