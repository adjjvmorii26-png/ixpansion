"""Experiment Marketplace — publish, discover, and monetize experiments.

Users can publish their own experiments, set prices, and earn revenue
through the marketplace. The platform takes a 20% commission.

Usage:
    GET  /api/marketplace/list          — browse experiments
    POST /api/marketplace/publish       — publish an experiment
    GET  /api/marketplace/<id>          — get experiment details
    POST /api/marketplace/<id>/purchase — purchase an experiment
    GET  /api/marketplace/earnings      — view earnings (creator)
"""
from __future__ import annotations

import hashlib
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MARKETPLACE_FILE = ROOT / ".runtime" / "marketplace.json"
EARNINGS_FILE = ROOT / ".runtime" / "earnings.json"

COMMISSION_RATE = 0.20  # 20% platform commission

CATEGORIES = [
    "quantum", "ecology", "folklore", "cosmology", "biology",
    "chaos", "information", "geometry", "linguistics", "meta",
]


def _ensure_files():
    MARKETPLACE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not MARKETPLACE_FILE.exists():
        MARKETPLACE_FILE.write_text("[]")
    if not EARNINGS_FILE.exists():
        EARNINGS_FILE.write_text("{}")


def _load_items() -> List[Dict]:
    _ensure_files()
    return json.loads(MARKETPLACE_FILE.read_text())


def _save_items(items: List[Dict]):
    _ensure_files()
    MARKETPLACE_FILE.write_text(json.dumps(items, indent=2))


def _load_earnings() -> Dict:
    _ensure_files()
    return json.loads(EARNINGS_FILE.read_text())


def _save_earnings(earnings: Dict):
    _ensure_files()
    EARNINGS_FILE.write_text(json.dumps(earnings, indent=2))


def publish_experiment(name: str, creator: str, description: str,
                       category: str, free_access: float,
                       code_hash: str = "", tags: List[str] = None) -> Dict:
    if free_access < 0:
        return {"error": "price must be non-negative"}
    if category not in CATEGORIES:
        return {"error": f"unknown category: {category}"}
    item_id = hashlib.sha256(f"{name}:{creator}:{time.time()}".encode()).hexdigest()[:12]
    item = {
        "id": item_id,
        "name": name,
        "creator": creator,
        "description": description,
        "category": category,
        "free_access": free_access,
        "code_hash": code_hash,
        "tags": tags or [],
        "created": time.time(),
        "purchases": 0,
        "rating": 0.0,
        "rating_count": 0,
        "featured": False,
    }
    items = _load_items()
    items.append(item)
    _save_items(items)
    return {"published": True, "id": item_id, "name": name}


def list_experiments(category: str = None, sort_by: str = "popular",
                     limit: int = 20) -> Dict:
    items = _load_items()
    if category:
        items = [i for i in items if i["category"] == category]
    if sort_by == "popular":
        items.sort(key=lambda i: i["purchases"], reverse=True)
    elif sort_by == "price_low":
        items.sort(key=lambda i: i["free_access"])
    elif sort_by == "price_high":
        items.sort(key=lambda i: i["free_access"], reverse=True)
    elif sort_by == "rating":
        items.sort(key=lambda i: i["rating"], reverse=True)
    elif sort_by == "newest":
        items.sort(key=lambda i: i["created"], reverse=True)
    return {"experiments": items[:limit], "total": len(items)}


def get_experiment(item_id: str) -> Optional[Dict]:
    items = _load_items()
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def purchase_experiment(item_id: str, buyer: str) -> Dict:
    items = _load_items()
    for item in items:
        if item["id"] == item_id:
            if item["free_access"] == 0:
                commission = 0
                creator_payout = 0
            else:
                commission = item["free_access"] * COMMISSION_RATE
                creator_payout = item["free_access"] - commission
            item["purchases"] += 1
            _save_items(items)

            earnings = _load_earnings()
            creator = item["creator"]
            if creator not in earnings:
                earnings[creator] = {"total": 0, "transactions": []}
            earnings[creator]["total"] += creator_payout
            earnings[creator]["transactions"].append({
                "item": item["name"],
                "payout": creator_payout,
                "commission": commission,
                "buyer": buyer,
                "time": time.time(),
            })
            _save_earnings(earnings)
            return {
                "purchased": True,
                "item": item["name"],
                "price": item["free_access"],
                "commission": commission,
                "creator_payout": creator_payout,
            }
    return {"error": "item not found"}


def get_earnings(creator: str) -> Dict:
    earnings = _load_earnings()
    return earnings.get(creator, {"total": 0, "transactions": []})


def featured_experiments() -> List[Dict]:
    items = _load_items()
    return [i for i in items if i.get("featured", False)]


def handler(request, response):
    """API handler for marketplace endpoints."""
    return {"message": "Marketplace API", "categories": CATEGORIES}


def demo():
    print("=== Experiment Marketplace ===")
    publish_experiment("quantum_bloom", "aleph",
                       "Quantum-inspired bloom filter with decoherence",
                       "quantum", 4.99, tags=["quantum", "bloom", "filter"])
    publish_experiment("coral_optimizer", "aleph",
                       "Ant colony optimization using coral reef dynamics",
                       "ecology", 0, tags=["optimization", "ecology"])
    publish_experiment("sacred_code", "contributor1",
                       "Generate sacred geometry from code structure",
                       "geometry", 9.99, tags=["geometry", "visualization"])

    listing = list_experiments()
    print(f"  Listed {listing['total']} experiments")
    for exp in listing["experiments"]:
        print(f"    {exp['name']}: ${exp['free_access']}, "
              f"purchases={exp['purchases']}")

    result = purchase_experiment(listing["experiments"][0]["id"], "buyer_1")
    print(f"\n  Purchase: {result}")

    earnings = get_earnings("aleph")
    print(f"\n  Creator earnings: ${earnings['total']:.2f}")
    print(f"  Transactions: {len(earnings['transactions'])}")

    return {"listing": listing, "earnings": earnings}


if __name__ == "__main__":
    demo()
