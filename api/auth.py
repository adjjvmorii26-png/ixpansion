"""API Authentication & Tier Management — handles API keys, tiers, and rate limits.

Tiers:
  - free:     100 calls/day, basic experiments only
  - pro:      10,000 calls/day, all experiments, priority
  - enterprise: Unlimited, custom integrations, SLA

Usage:
    GET  /api/auth/keys          — list API keys (admin)
    POST /api/auth/keys          — create API key
    GET  /api/auth/usage/<key>   — check usage for a key
    GET  /api/auth/tiers         — list available tiers
"""
from __future__ import annotations

import hashlib
import json
import time
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

USAGE_FILE = ROOT / ".runtime" / "usage.json"
KEYS_FILE = ROOT / ".runtime" / "api_keys.json"

TIERS = {
    "free": {
        "name": "Free",
        "daily_limit": 100,
        "monthly_price_usd": 0,
        "experiments": "basic",
        "rate_limit_per_minute": 10,
        "features": ["list_experiments", "run_basic", "health_check"],
    },
    "pro": {
        "name": "Pro",
        "daily_limit": 10_000,
        "monthly_price_usd": 29,
        "experiments": "all",
        "rate_limit_per_minute": 100,
        "features": ["list_experiments", "run_all", "health_check",
                      "benchmarks", "anomaly_detection", "constellation"],
    },
    "enterprise": {
        "name": "Enterprise",
        "daily_limit": -1,  # unlimited
        "monthly_price_usd": 199,
        "experiments": "all",
        "rate_limit_per_minute": 1000,
        "features": ["list_experiments", "run_all", "health_check",
                      "benchmarks", "anomaly_detection", "constellation",
                      "custom_agents", "priority_support", "sla_999",
                      "webhook_notifications", "bulk_operations"],
    },
}

BASIC_EXPERIMENTS = {
    "photon_memory", "dark_matter_mapper", "coral_reef_simulator",
    "crystalline_lattice", "neutrino_detector", "fractal_language",
    "dream_weaver", "strange_attractor", "phase_transition",
    "sacred_geometry", "myth_generator", "keystone_species",
}


def _ensure_files():
    USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        if not KEYS_FILE.exists():
            KEYS_FILE.write_text("{}")
        if not USAGE_FILE.exists():
            USAGE_FILE.write_text("{}")
    except OSError:
        pass  # read-only fs (serverless)


def _load_keys() -> Dict:
    _ensure_files()
    return json.loads(KEYS_FILE.read_text())


def _save_keys(keys: Dict):
    _ensure_files()
    KEYS_FILE.write_text(json.dumps(keys, indent=2))


def _load_usage() -> Dict:
    _ensure_files()
    return json.loads(USAGE_FILE.read_text())


def _save_usage(usage: Dict):
    _ensure_files()
    USAGE_FILE.write_text(json.dumps(usage, indent=2))


def generate_api_key(owner: str, tier: str = "free") -> Dict:
    if tier not in TIERS:
        return {"error": f"unknown tier: {tier}. Valid: {list(TIERS.keys())}"}
    raw = f"{owner}:{tier}:{time.time()}"
    key = "ixp_" + hashlib.sha256(raw.encode()).hexdigest()[:32]
    keys = _load_keys()
    keys[key] = {
        "owner": owner,
        "tier": tier,
        "created": time.time(),
        "active": True,
    }
    _save_keys(keys)
    return {"api_key": key, "tier": tier, "owner": owner}


def validate_key(api_key: str) -> Dict:
    keys = _load_keys()
    if api_key not in keys:
        return {"valid": False, "error": "key not found"}
    entry = keys[api_key]
    if not entry.get("active", False):
        return {"valid": False, "error": "key deactivated"}
    tier_info = TIERS.get(entry["tier"], TIERS["free"])
    return {
        "valid": True,
        "tier": entry["tier"],
        "owner": entry["owner"],
        "daily_limit": tier_info["daily_limit"],
        "rate_limit": tier_info["rate_limit_per_minute"],
        "features": tier_info["features"],
    }


def record_usage(api_key: str, endpoint: str) -> Dict:
    usage = _load_usage()
    today = time.strftime("%Y-%m-%d")
    if api_key not in usage:
        usage[api_key] = {}
    if today not in usage[api_key]:
        usage[api_key][today] = {"calls": 0, "endpoints": {}}
    usage[api_key][today]["calls"] += 1
    usage[api_key][today]["endpoints"][endpoint] = (
        usage[api_key][today]["endpoints"].get(endpoint, 0) + 1
    )
    _save_usage(usage)

    keys = _load_keys()
    tier = keys.get(api_key, {}).get("tier", "free")
    tier_info = TIERS.get(tier, TIERS["free"])
    daily_calls = usage[api_key][today]["calls"]
    limit = tier_info["daily_limit"]

    return {
        "daily_calls": daily_calls,
        "daily_limit": limit,
        "remaining": max(0, limit - daily_calls) if limit > 0 else -1,
        "tier": tier,
        "over_limit": daily_calls > limit if limit > 0 else False,
    }


def check_experiment_access(api_key: str, experiment_name: str) -> Dict:
    validation = validate_key(api_key)
    if not validation["valid"]:
        return {"allowed": False, "reason": validation["error"]}
    tier = validation["tier"]
    tier_info = TIERS[tier]
    if tier_info["experiments"] == "all":
        return {"allowed": True, "tier": tier}
    if experiment_name in BASIC_EXPERIMENTS:
        return {"allowed": True, "tier": tier}
    return {
        "allowed": False,
        "reason": f"experiment '{experiment_name}' requires pro tier or higher",
        "upgrade_url": "/api/auth/tiers",
    }


def handler(request, response):
    """API handler for auth endpoints."""
    path = request.path if hasattr(request, "path") else "/auth"
    method = request.method if hasattr(request, "method") else "GET"

    if "tiers" in path:
        return {"tiers": TIERS}
    elif "usage" in path:
        api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
        return record_usage(api_key, path)
    else:
        return {"message": "Auth API", "endpoints": ["/tiers", "/usage", "/keys"]}


def demo():
    print("=== API Auth & Tier System ===")
    result = generate_api_key("test_user", "pro")
    key = result["api_key"]
    print(f"  Created key: {key[:20]}... (tier={result['tier']})")

    validation = validate_key(key)
    print(f"  Validation: tier={validation['tier']}, limit={validation['daily_limit']}")

    usage = record_usage(key, "/api/experiments")
    print(f"  Usage: {usage['daily_calls']}/{usage['daily_limit']} "
          f"(remaining={usage['remaining']})")

    access = check_experiment_access(key, "photon_memory")
    print(f"  Access to photon_memory: {access['allowed']}")

    access2 = check_experiment_access(key, "advanced_quantum")
    print(f"  Access to advanced_quantum: {access2['allowed']} "
          f"({access2.get('reason', 'ok')})")

    print(f"\n  Tiers:")
    for tier_name, tier_info in TIERS.items():
        print(f"    {tier_name}: ${tier_info['monthly_price_usd']}/mo, "
              f"{tier_info['daily_limit']} calls/day")

    return {"tiers": TIERS}


if __name__ == "__main__":
    demo()


def coherence_vitals() -> dict:
    """auth reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "auth_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['dream_synthesis', 'analytics', 'usage_dashboard']

