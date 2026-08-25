"""Paradox Marketplace — buy and sell contradictions that produce innovations.

When system states contradict each other, they create productive tension.
This marketplace lets users submit paradoxes, bid to resolve them, and
collect the innovations that emerge from resolution.

Usage:
    POST /api/paradox/submit       — submit a paradox
    POST /api/paradox/resolve      — attempt to resolve a paradox
    GET  /api/paradox/open         — list unresolved paradoxes
    GET  /api/paradox/resolved     — list resolved paradoxes
    GET  /api/paradox/stats        — marketplace statistics
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

RESOLUTION_STRATEGIES = [
    "transcendence",  # Both true at a higher abstraction
    "reframing",      # The contradiction was illusory
    "synthesis",      # A new truth emerges from both
    "layer_split",    # Each is true in its own domain
    "temporal_shift", # One is true now, one later
    "meta_resolution", # The paradox itself is the insight
]

INNOVATION_TYPES = [
    "new_experiment_template",
    "novel_agent_behavior",
    "unexpected_system_property",
    "cross_module_bridge",
    "emergent_metric",
    "paradox_derived_algorithm",
    "contradiction_harvested_as_fuel",
]


class ParadoxMarketplace:
    def __init__(self):
        self.paradoxes: Dict[str, Dict] = {}
        self.history: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "paradox_market.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.paradoxes = data.get("paradoxes", {})
            self.history = data.get("history", [])

    def _save(self):
        path = ROOT / ".runtime" / "paradox_market.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "paradoxes": self.paradoxes,
            "history": self.history[-500:],
        }, indent=2))

    def submit(self, submitter: str, statement_a: str,
               statement_b: str, domain: str = "general",
               bounty: float = 10.0) -> Dict:
        paradox_id = hashlib.sha256(f"{statement_a}:{statement_b}:{time.time()}".encode()).hexdigest()[:10]
        tension = abs(hash(statement_a) - hash(statement_b)) % 1000 / 1000.0
        self.paradoxes[paradox_id] = {
            "submitter": submitter,
            "statement_a": statement_a,
            "statement_b": statement_b,
            "domain": domain,
            "bounty": bounty,
            "tension": round(tension, 4),
            "resolution_attempts": [],
            "status": "open",
            "created": time.time(),
        }
        self._save()
        return {
            "paradox_id": paradox_id,
            "tension": round(tension, 4),
            "bounty": bounty,
        }

    def resolve(self, paradox_id: str, resolver: str,
                resolution: str = "", strategy: str = "synthesis") -> Dict:
        if paradox_id not in self.paradoxes:
            return {"error": "paradox not found"}
        paradox = self.paradoxes[paradox_id]
        if paradox["status"] == "resolved":
            return {"error": "already resolved"}
        if strategy not in RESOLUTION_STRATEGIES:
            strategy = "synthesis"
        paradox["resolution_attempts"].append({
            "resolver": resolver,
            "resolution": resolution,
            "strategy": strategy,
            "timestamp": time.time(),
        })
        success_prob = 0.3 + paradox["tension"] * 0.4 + random.uniform(0, 0.3)
        succeeded = random.random() < success_prob
        if succeeded:
            paradox["status"] = "resolved"
            paradox["resolved_by"] = resolver
            paradox["resolution_strategy"] = strategy
            paradox["resolved_at"] = time.time()
            innovation = random.choice(INNOVATION_TYPES)
            result = {
                "resolved": True,
                "paradox_id": paradox_id,
                "strategy": strategy,
                "innovation": innovation,
                "bounty_earned": paradox["bounty"],
                "insight": f"Paradox resolved via {strategy}: {innovation}",
            }
        else:
            result = {
                "resolved": False,
                "paradox_id": paradox_id,
                "attempts": len(paradox["resolution_attempts"]),
                "message": f"Resolution failed. Try a different strategy. Tension: {paradox['tension']}",
            }
        self.history.append({**result, "timestamp": time.time()})
        self._save()
        return result

    def list_open(self) -> List[Dict]:
        return [
            {"id": k, **v} for k, v in self.paradoxes.items()
            if v["status"] == "open"
        ]

    def list_resolved(self) -> List[Dict]:
        return [
            {"id": k, **v} for k, v in self.paradoxes.items()
            if v["status"] == "resolved"
        ]

    def stats(self) -> Dict:
        total = len(self.paradoxes)
        resolved = sum(1 for p in self.paradoxes.values() if p["status"] == "resolved")
        total_bounty = sum(p["bounty"] for p in self.paradoxes.values() if p["status"] == "resolved")
        return {
            "total_paradoxes": total,
            "resolved": resolved,
            "open": total - resolved,
            "total_bounty_distributed": total_bounty,
            "resolution_rate": round(resolved / max(total, 1), 4),
        }


def handler(request, response):
    pm = ParadoxMarketplace()
    return pm.stats()


def demo():
    pm = ParadoxMarketplace()
    print("=== Paradox Marketplace ===")
    p = pm.submit("user_1",
                  "The system must be deterministic to be reliable",
                  "The system must be random to be creative",
                  domain="core_philosophy", bounty=50)
    print(f"\nParadox submitted: {p['paradox_id']}")
    print(f"Tension: {p['tension']}, Bounty: {p['bounty']} credits")

    result = pm.resolve(p["paradox_id"], "philosopher_1",
                        resolution="Determinism provides the canvas, randomness paints on it",
                        strategy="synthesis")
    if result.get("resolved"):
        print(f"\nRESOLVED via {result['strategy']}!")
        print(f"Innovation: {result['innovation']}")
        print(f"Bounty earned: {result['bounty_earned']} credits")
    else:
        print(f"\nFailed: {result['message']}")

    stats = pm.stats()
    print(f"\nMarketplace: {stats['total_paradoxes']} paradoxes, "
          f"{stats['resolved']} resolved, "
          f"{stats['total_bounty_distributed']} credits distributed")

    return stats


if __name__ == "__main__":
    demo()
