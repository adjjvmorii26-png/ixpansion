"""Live Usage Dashboard — real-time usage visualization data.

Provides streaming data for the dashboard: live API call counts,
experiment execution status, credit balances, and revenue graphs.

Usage:
    GET /api/usage/live       — live metrics snapshot
    GET /api/usage/history    — historical usage data
    GET /api/usage/top        — top experiments/users
"""
from __future__ import annotations

import hashlib
import json
import time
import math
import sys
from pathlib import Path
from typing import Any, Dict, List
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

USAGE_FILE = ROOT / ".runtime" / "usage.json"
CREDITS_FILE = ROOT / ".runtime" / "credit_balances.json"
MARKETPLACE_FILE = ROOT / ".runtime" / "marketplace.json"


def _load_json(path: Path) -> Any:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def get_live_metrics() -> Dict:
    usage = _load_json(USAGE_FILE)
    today = time.strftime("%Y-%m-%d")
    total_today = 0
    active_users = set()
    endpoint_counts = Counter()
    for key, days in usage.items():
        if today in days:
            total_today += days[today].get("calls", 0)
            active_users.add(key)
            for ep, count in days[today].get("endpoints", {}).items():
                endpoint_counts[ep] += count

    experiment_dir = ROOT / "lab" / "experiments"
    total_experiments = len(list(experiment_dir.glob("*.py"))) - 1 if experiment_dir.exists() else 0

    test_dir = ROOT / "lab" / "tests"
    total_tests = len(list(test_dir.glob("test_*.py"))) if test_dir.exists() else 0

    marketplace = _load_json(MARKETPLACE_FILE)
    total_listings = len(marketplace) if isinstance(marketplace, list) else 0

    return {
        "timestamp": time.time(),
        "api_calls_today": total_today,
        "active_users": len(active_users),
        "total_experiments": total_experiments,
        "total_tests": total_tests,
        "marketplace_listings": total_listings,
        "top_endpoints": endpoint_counts.most_common(5),
        "status": "operational",
    }


def get_history(days: int = 7) -> List[Dict]:
    usage = _load_json(USAGE_FILE)
    history = []
    for i in range(days):
        day = time.strftime("%Y-%m-%d", time.gmtime(time.time() - i * 86400))
        day_total = 0
        for key, data in usage.items():
            if day in data:
                day_total += data[day].get("calls", 0)
        history.append({"date": day, "calls": day_total})
    return list(reversed(history))


def get_top_users(limit: int = 10) -> List[Dict]:
    usage = _load_json(USAGE_FILE)
    user_totals = []
    for key, days in usage.items():
        total = sum(d.get("calls", 0) for d in days.values())
        user_totals.append({"api_key": key[:12] + "...", "total_calls": total})
    return sorted(user_totals, key=lambda x: x["total_calls"], reverse=True)[:limit]


def handler(request, response):
    return get_live_metrics()


def demo():
    print("=== Live Usage Dashboard ===")
    metrics = get_live_metrics()
    print(f"\nLive metrics:")
    print(f"  API calls today: {metrics['api_calls_today']}")
    print(f"  Active users: {metrics['active_users']}")
    print(f"  Experiments: {metrics['total_experiments']}")
    print(f"  Tests: {metrics['total_tests']}")
    print(f"  Marketplace: {metrics['marketplace_listings']} listings")
    print(f"  Status: {metrics['status']}")

    history = get_history(3)
    print(f"\nHistory ({len(history)} days):")
    for h in history:
        bar = "█" * min(h["calls"], 50)
        print(f"  {h['date']}: {h['calls']:>5} {bar}")

    return metrics


if __name__ == "__main__":
    demo()
