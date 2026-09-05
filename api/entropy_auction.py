"""Entropy Auction — bid for the right to inject controlled chaos.

Users bid on entropy slots — specific subsystems they want to destabilize
for creative purposes. Higher bids get more chaos authority. The system
monitors outcomes and reports emergent innovations from chaos.

Usage:
    POST /api/entropy/auction      — start an auction for a subsystem
    POST /api/entropy/bid          — place a bid
    POST /api/entropy/resolve      — resolve auction, grant chaos rights
    GET  /api/entropy/active       — active auctions
    GET  /api/entropy/outcomes     — chaos outcomes from past auctions
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CHAOS_OUTCOMES = [
    "unexpected_module_emergence",
    "cross_domain_resonance_spike",
    "paradox_resolved_productively",
    "new_experiment_category_created",
    "agent_behavior_evolution",
    "topology_shift_detected",
    "entropy_harvested_as_energy",
    "system_self_healed",
    "emergent_language_detected",
    "creative_breakthrough_logged",
]


class EntropyAuction:
    def __init__(self):
        self.auctions: Dict[str, Dict] = {}
        self.outcomes: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "entropy_auction.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.auctions = data.get("auctions", {})
            self.outcomes = data.get("outcomes", [])

    def _save(self):
        path = ROOT / ".runtime" / "entropy_auction.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "auctions": self.auctions,
            "outcomes": self.outcomes[-500:],
        }, indent=2))

    def create_auction(self, subsystem: str, creator: str,
                       max_chaos: float = 0.5, duration_sec: int = 300) -> Dict:
        auction_id = hashlib.sha256(f"{subsystem}:{time.time()}".encode()).hexdigest()[:10]
        self.auctions[auction_id] = {
            "subsystem": subsystem,
            "creator": creator,
            "max_chaos": min(max_chaos, 1.0),
            "bids": [],
            "created": time.time(),
            "duration_sec": duration_sec,
            "status": "open",
        }
        self._save()
        return {
            "auction_id": auction_id,
            "subsystem": subsystem,
            "max_chaos": min(max_chaos, 1.0),
            "duration_sec": duration_sec,
        }

    def bid(self, auction_id: str, bidder: str, amount: float,
            chaos_level: float = 0.3) -> Dict:
        if auction_id not in self.auctions:
            return {"error": f"unknown auction: {auction_id}"}
        auction = self.auctions[auction_id]
        if auction["status"] != "open":
            return {"error": "auction is closed"}
        if chaos_level > auction["max_chaos"]:
            return {"error": f"chaos level exceeds max ({auction['max_chaos']})"}
        bid = {
            "bidder": bidder,
            "amount": amount,
            "chaos_level": chaos_level,
            "timestamp": time.time(),
        }
        auction["bids"].append(bid)
        auction["bids"].sort(key=lambda b: b["amount"], reverse=True)
        self._save()
        return {
            "auction_id": auction_id,
            "bid_amount": amount,
            "chaos_level": chaos_level,
            "position": next(
                (i + 1 for i, b in enumerate(auction["bids"]) if b["bidder"] == bidder), -1
            ),
        }

    def resolve(self, auction_id: str) -> Dict:
        if auction_id not in self.auctions:
            return {"error": f"unknown auction: {auction_id}"}
        auction = self.auctions[auction_id]
        if auction["status"] != "open":
            return {"error": "already resolved"}
        if not auction["bids"]:
            auction["status"] = "expired"
            self._save()
            return {"auction_id": auction_id, "status": "expired", "reason": "no bids"}
        winner = auction["bids"][0]
        chaos_used = winner["chaos_level"]
        num_outcomes = random.randint(1, 3)
        selected_outcomes = random.sample(CHAOS_OUTCOMES, min(num_outcomes, len(CHAOS_OUTCOMES)))
        innovation_score = round(chaos_used * random.uniform(0.5, 1.5), 4)
        outcome = {
            "auction_id": auction_id,
            "winner": winner["bidder"],
            "winning_bid": winner["amount"],
            "chaos_injected": chaos_used,
            "subsystem": auction["subsystem"],
            "outcomes": selected_outcomes,
            "innovation_score": innovation_score,
            "resolved_at": time.time(),
        }
        auction["status"] = "resolved"
        auction["winner"] = winner["bidder"]
        self.outcomes.append(outcome)
        self._save()
        return outcome

    def list_active(self) -> List[Dict]:
        return [{"id": k, **v} for k, v in self.auctions.items() if v["status"] == "open"]

    def recent_outcomes(self, limit: int = 10) -> List[Dict]:
        return self.outcomes[-limit:]


def handler(request, response):
    ea = EntropyAuction()
    return {"active": len(ea.list_active()), "outcomes": len(ea.outcomes)}


def demo():
    ea = EntropyAuction()
    print("=== Entropy Auction ===")
    auc = ea.create_auction("quantum_tunneling", "system", max_chaos=0.6)
    print(f"\nAuction created: {auc['auction_id']} for '{auc['subsystem']}'")

    ea.bid(auc["auction_id"], "researcher_1", 100, chaos_level=0.3)
    ea.bid(auc["auction_id"], "researcher_2", 250, chaos_level=0.5)
    ea.bid(auc["auction_id"], "researcher_3", 150, chaos_level=0.4)
    print("3 bids placed")

    result = ea.resolve(auc["auction_id"])
    print(f"\nWinner: {result['winner']} (bid: {result['winning_bid']})")
    print(f"Chaos injected: {result['chaos_injected']}")
    print(f"Innovation score: {result['innovation_score']}")
    print(f"Outcomes: {', '.join(result['outcomes'])}")

    return {"auctions": len(ea.auctions), "outcomes": len(ea.outcomes)}


if __name__ == "__main__":
    demo()

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "0", "module": "entropy_auction"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
