"""API Key management — generate, validate, tier-based access.

Keys follow the format: ixp_<tier>_<random>
Tiers: free, growth, enterprise
"""
from __future__ import annotations

import hashlib
import json
import secrets
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
KEYS_FILE = ROOT / "gateway" / "keys.json"

TIER_LIMITS = {
    "free":       {"rpm": 10, "daily": 1000, "monthly": 30000},
    "growth":     {"rpm": 60, "daily": 10000, "monthly": 300000},
    "enterprise": {"rpm": 600, "daily": 100000, "monthly": 3000000},
}

TIER_FEATURES = {
    "free":       ["echo", "health", "modules", "poem", "intent", "meter"],
    "growth":     ["echo", "health", "modules", "poem", "intent", "meter",
                   "forecast", "garden", "gossip_uptime", "data_complexity",
                   "ledger", "platform_failure", "revelations", "capsule",
                   "song", "service_numinous", "temperament_origin"],
    "enterprise": ["*"],  # full access
}

TIER_PRICES = {
    "free":       {"monthly": 0, "overage_per_1k": 0},
    "growth":     {"monthly": 19, "overage_per_1k": 0.05},
    "enterprise": {"monthly": 99, "overage_per_1k": 0.01},
}


def _load_keys() -> Dict[str, Dict[str, Any]]:
    if not KEYS_FILE.exists():
        return {}
    try:
        return json.loads(KEYS_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _save_keys(keys: Dict[str, Dict[str, Any]]) -> None:
    KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
    KEYS_FILE.write_text(json.dumps(keys, indent=2))


def generate_key(owner: str, tier: str = "free") -> Dict[str, Any]:
    """Generate a new API key."""
    if tier not in TIER_LIMITS:
        raise ValueError(f"Invalid tier: {tier}. Must be one of: {list(TIER_LIMITS.keys())}")

    random_part = secrets.token_hex(16)
    key = f"ixp_{tier}_{random_part}"

    entry = {
        "key_hash": hashlib.sha256(key.encode()).hexdigest(),
        "key_prefix": key[:20] + "…",
        "owner": owner,
        "tier": tier,
        "created_at": time.time(),
        "last_used_at": None,
        "total_calls": 0,
        "monthly_calls": 0,
        "daily_calls": 0,
        "monthly_reset": _next_month_start(),
        "daily_reset": _next_day_start(),
    }

    keys = _load_keys()
    keys[entry["key_hash"]] = entry
    _save_keys(keys)
    return {"key": key, "owner": owner, "tier": tier, "limits": TIER_LIMITS[tier]}


def validate_key(key: str) -> Optional[Dict[str, Any]]:
    """Validate an API key. Returns key data if valid, None otherwise."""
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    keys = _load_keys()
    entry = keys.get(key_hash)
    if not entry:
        return None

    tier = entry.get("tier", "free")
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    now = time.time()

    # daily reset
    if now > entry.get("daily_reset", 0):
        entry["daily_calls"] = 0
        entry["daily_reset"] = _next_day_start()

    # monthly reset
    if now > entry.get("monthly_reset", 0):
        entry["monthly_calls"] = 0
        entry["monthly_reset"] = _next_month_start()

    entry["last_used_at"] = now
    entry["total_calls"] = entry.get("total_calls", 0) + 1
    entry["daily_calls"] = entry.get("daily_calls", 0) + 1
    entry["monthly_calls"] = entry.get("monthly_calls", 0) + 1

    keys[key_hash] = entry
    _save_keys(keys)

    entry["limits"] = limits
    entry["features"] = TIER_FEATURES.get(tier, TIER_FEATURES["free"])
    entry["key_prefix"] = entry.get("key_prefix", key[:20] + "…")
    return entry


def can_access(key_data: Dict[str, Any], module: str) -> bool:
    """Check if a key's tier allows access to a module."""
    features = key_data.get("features", [])
    if "*" in features:
        return True
    return module in features


def get_stats(key: str) -> Optional[Dict[str, Any]]:
    """Get stats for a key without incrementing the counter."""
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    keys = _load_keys()
    entry = keys.get(key_hash)
    if not entry:
        return None
    tier = entry.get("tier", "free")
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    return {
        "owner": entry["owner"],
        "tier": tier,
        "created_at": entry["created_at"],
        "last_used_at": entry.get("last_used_at"),
        "total_calls": entry.get("total_calls", 0),
        "daily_calls": entry.get("daily_calls", 0),
        "daily_limit": limits["daily"],
        "monthly_calls": entry.get("monthly_calls", 0),
        "monthly_limit": limits["monthly"],
        "features": TIER_FEATURES.get(tier, []),
    }


def list_keys() -> List[Dict[str, Any]]:
    """List all keys (admin use — no secret keys exposed)."""
    keys = _load_keys()
    return [
        {"owner": v["owner"], "tier": v["tier"],
         "key_prefix": v.get("key_prefix", ""),
         "total_calls": v.get("total_calls", 0),
         "created_at": v["created_at"]}
        for v in keys.values()
    ]


def _next_month_start() -> float:
    import datetime
    now = time.time()
    dt = datetime.datetime.fromtimestamp(now, tz=datetime.timezone.utc)
    if dt.month == 12:
        nxt = datetime.datetime(dt.year + 1, 1, 1, tzinfo=datetime.timezone.utc)
    else:
        nxt = datetime.datetime(dt.year, dt.month + 1, 1, tzinfo=datetime.timezone.utc)
    return nxt.timestamp()


def _next_day_start() -> float:
    import datetime
    now = time.time()
    dt = datetime.datetime.fromtimestamp(now, tz=datetime.timezone.utc)
    tomorrow = (dt + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return tomorrow.timestamp()
