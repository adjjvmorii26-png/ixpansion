from __future__ import annotations
"""Module Marketplace — tiered API access to organism modules."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MARKET_LOG = os.path.join(DATA_DIR, "module_market.json")

TIERS = ["free", "standard", "premium", "legendary"]
MODULE_CATALOG = [
    {"module": "coherence_regulator", "tier": "free", "price": 0, "usage_points": 1},
    {"module": "entropy_spike", "tier": "free", "price": 0, "usage_points": 1},
    {"module": "consciousness_stream", "tier": "free", "price": 0, "usage_points": 2},
    {"module": "mythopoetic_engine", "tier": "free", "price": 0, "usage_points": 2},
    {"module": "dream_logic_physics", "tier": "standard", "price": 50, "usage_points": 5},
    {"module": "paradox_synthesis", "tier": "standard", "price": 50, "usage_points": 5},
    {"module": "resonance_graph", "tier": "premium", "price": 200, "usage_points": 10},
    {"module": "entropy_oracle", "tier": "premium", "price": 200, "usage_points": 10},
    {"module": "chrono_forge", "tier": "premium", "price": 200, "usage_points": 10},
    {"module": "lucid_session", "tier": "premium", "price": 300, "usage_points": 15},
    {"module": "lucid_dungeon", "tier": "premium", "price": 300, "usage_points": 15},
    {"module": "hex_language", "tier": "legendary", "price": 1000, "usage_points": 25},
    {"module": "phase_weaver", "tier": "legendary", "price": 1000, "usage_points": 25},
    {"module": "self_repair_network", "tier": "legendary", "price": 1000, "usage_points": 25},
]

def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except: return d or {}
def _save(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f: json.dump(d, f, indent=2)

def catalog() -> dict:
    return {"action": "catalog", "modules": MODULE_CATALOG, "count": len(MODULE_CATALOG),
            "tiers": {t: sum(1 for m in MODULE_CATALOG if m["tier"] == t) for t in TIERS}}

def subscribe(tier: str = "standard") -> dict:
    log = _load(MARKET_LOG, {"subscriptions": [], "total": 0})
    prices = {"free": 0, "standard": 10, "premium": 29, "legendary": 99}
    tier = tier if tier in prices else "standard"
    sub = {
        "id": hashlib.sha256(f"sub:{tier}:{time.time()}".encode()).hexdigest()[:10],
        "tier": tier, "price_usd": prices[tier],
        "modules_unlocked": [m["module"] for m in MODULE_CATALOG if m["tier"] in ("free", tier)],
        "usage_points_monthly": {"free": 100, "standard": 1000, "premium": 5000, "legendary": 25000}[tier],
        "status": "active", "timestamp": time.time(),
    }
    log["subscriptions"].append(sub)
    log["total"] += 1
    _save(MARKET_LOG, log)
    return {"action": "subscribe", "subscription": sub}

def access(module: str, tier: str = "free") -> dict:
    entry = next((m for m in MODULE_CATALOG if m["module"] == module), None)
    if not entry: return {"error": "module not found"}
    tier_rank = {"free": 0, "standard": 1, "premium": 2, "legendary": 3}
    module_tier_rank = tier_rank[entry["tier"]]
    user_tier_rank = tier_rank.get(tier, 0)
    granted = user_tier_rank >= module_tier_rank
    return {"action": "access", "module": module, "requested_tier": tier, "required_tier": entry["tier"],
            "price": entry["price"], "usage_points": entry["usage_points"], "granted": granted,
            "message": "Access granted" if granted else f"Requires {entry['tier']} tier (upgrade from {tier})"}

def coherence_vitals() -> dict:
    return {"layer": "economy", "status": "active", "resonance": 0.7, "wave": "368"}
def resonates_with() -> list:
    return ["organism_token", "lucid_session"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/catalog")
    if path == "/catalog": return catalog()
    elif path == "/subscribe": return subscribe(payload.get("tier", "standard"))
    elif path == "/access": return access(payload.get("module", ""), payload.get("tier", "free"))
    return {"error": "unknown", "available": ["/catalog", "/subscribe", "/access"]}
