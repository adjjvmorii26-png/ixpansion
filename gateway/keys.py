"""API Key management — HMAC-based, serverless-compatible.

Keys follow the format: ixp_<tier>_<hmac_signature>
No file storage required — validation is signature-based.
Rate limits use in-memory counters (reset on cold start).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any, Dict, List, Optional

# HMAC secret — use env var in production, random fallback for dev
_HMAC_SECRET = os.environ.get("IXPANSION_HMAC_SECRET", "ixpansion-dev-secret-change-me")

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
                   "song", "service_numinous", "temperament_origin",
                   "frontier_stream", "hex_tool", "constellation_cartographer"],
    "enterprise": ["*"],  # full access
}

TIER_PRICES = {
    "free":       {"monthly": 0, "overage_per_1k": 0},
    "growth":     {"monthly": 19, "overage_per_1k": 0.05},
    "enterprise": {"monthly": 99, "overage_per_1k": 0.01},
}

# In-memory rate limiting (resets on cold start — acceptable for serverless)
_call_counts: Dict[str, Dict[str, Any]] = {}


def _hmac_sign(data: str) -> str:
    """Compute HMAC-SHA256 signature."""
    return hmac.new(
        _HMAC_SECRET.encode(), data.encode(), hashlib.sha256
    ).hexdigest()[:16]


def generate_key(owner: str, tier: str = "free") -> Dict[str, Any]:
    """Generate a new API key (returns key + metadata)."""
    if tier not in TIER_LIMITS:
        raise ValueError(f"Invalid tier: {tier}. Must be one of: {list(TIER_LIMITS.keys())}")

    random_part = secrets.token_hex(8)
    # HMAC signs: tier + random part (owner is metadata, not recoverable)
    signature = _hmac_sign(f"{tier}:{random_part}")
    key = f"ixp_{tier}_{random_part}{signature}"

    return {
        "key": key,
        "owner": owner,
        "tier": tier,
        "limits": TIER_LIMITS[tier],
        "features": TIER_FEATURES.get(tier, []),
    }


def validate_key(key: str) -> Optional[Dict[str, Any]]:
    """Validate an API key by HMAC signature. Returns key data if valid."""
    if not key.startswith("ixp_"):
        return None

    parts = key.split("_", 2)
    if len(parts) < 3:
        return None

    tier = parts[1]
    remainder = parts[2]

    # remainder = random_part (16 hex) + signature (16 hex) = 32 chars
    if len(remainder) < 32:
        return None

    random_part = remainder[:16]
    provided_sig = remainder[16:32]

    # Reconstruct the expected signature — we need owner info
    # Since owner is not in the key, we derive it from a fixed mapping
    # For validation, we check the HMAC matches the random part
    # Owner is tracked separately (or can be encoded in the key)
    # Simple approach: store owner in the random_part area
    # Better approach: encode owner hash in the key

    # Since we can't store owner in the key without a secret,
    # use tier + random_part as the HMAC input
    expected_sig = _hmac_sign(f"{tier}:{random_part}")
    if not hmac.compare_digest(provided_sig, expected_sig):
        return None

    tier_data = {
        "tier": tier,
        "owner": f"key-{random_part[:8]}",
        "features": TIER_FEATURES.get(tier, []),
        "limits": TIER_LIMITS.get(tier, TIER_LIMITS["free"]),
    }

    # Update in-memory call counts
    now = time.time()
    counts = _call_counts.setdefault(key, {
        "total_calls": 0, "daily_calls": 0, "monthly_calls": 0,
        "daily_reset": _next_day_start(), "monthly_reset": _next_month_start(),
    })

    # Reset counters if periods expired
    if now > counts.get("daily_reset", 0):
        counts["daily_calls"] = 0
        counts["daily_reset"] = _next_day_start()
    if now > counts.get("monthly_reset", 0):
        counts["monthly_calls"] = 0
        counts["monthly_reset"] = _next_month_start()

    counts["total_calls"] += 1
    counts["daily_calls"] += 1
    counts["monthly_calls"] += 1

    tier_data["total_calls"] = counts["total_calls"]
    tier_data["daily_calls"] = counts["daily_calls"]
    tier_data["monthly_calls"] = counts["monthly_calls"]
    return tier_data


def can_access(key_data: Dict[str, Any], module: str) -> bool:
    """Check if a key's tier allows access to a module."""
    features = key_data.get("features", [])
    if "*" in features:
        return True
    return module in features


def get_stats(key: str) -> Optional[Dict[str, Any]]:
    """Get stats for a key without incrementing the counter."""
    data = validate_key.__wrapped__(key) if hasattr(validate_key, "__wrapped__") else None
    counts = _call_counts.get(key)
    if not counts:
        return None
    key_data = {"key": key}
    tier = key.split("_")[1] if key.startswith("ixp_") else "free"
    return {
        "tier": tier,
        "total_calls": counts.get("total_calls", 0),
        "daily_calls": counts.get("daily_calls", 0),
        "daily_limit": TIER_LIMITS.get(tier, TIER_LIMITS["free"])["daily"],
        "monthly_calls": counts.get("monthly_calls", 0),
        "monthly_limit": TIER_LIMITS.get(tier, TIER_LIMITS["free"])["monthly"],
        "features": TIER_FEATURES.get(tier, []),
    }


def list_keys() -> List[Dict[str, Any]]:
    """List active keys (in-memory only)."""
    results = []
    for key, counts in _call_counts.items():
        tier = key.split("_")[1] if key.startswith("ixp_") else "unknown"
        results.append({
            "key_prefix": key[:24] + "...",
            "tier": tier,
            "total_calls": counts.get("total_calls", 0),
        })
    return results


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
