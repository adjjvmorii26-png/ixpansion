"""Entropy Weaver — threads chaos and order into balanced tapestries.

The Entropy Weaver doesn't fight chaos or enforce order — it weaves
them together into balanced patterns. Too much order creates stagnation;
too much chaos creates destruction. The Weaver finds the creative edge.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class EntropyThread:
    def __init__(self, name: str, chaos: float, order: float):
        self.name = name
        self.chaos = min(max(chaos, 0.0), 1.0)
        self.order = min(max(order, 0.0), 1.0)
        self.balance = 1.0 - abs(self.chaos - self.order)
        self.beauty = self.balance * (self.chaos + self.order) / 2

    def weave_with(self, other: "EntropyThread") -> Dict[str, Any]:
        new_chaos = (self.chaos + other.chaos) / 2
        new_order = (self.order + other.order) / 2
        combined = EntropyThread(f"{self.name}+{other.name}", new_chaos, new_order)
        return {
            "combined_name": combined.name,
            "chaos": round(combined.chaos, 3),
            "order": round(combined.order, 3),
            "balance": round(combined.balance, 3),
            "beauty": round(combined.beauty, 3),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "chaos": round(self.chaos, 3),
            "order": round(self.order, 3),
            "balance": round(self.balance, 3),
            "beauty": round(self.beauty, 3),
        }


class EntropyWeaver:
    def __init__(self):
        self.threads: List[EntropyThread] = []
        self.weavings: List[Dict[str, Any]] = []

    def create_thread(self, name: str, chaos: float = None, order: float = None) -> Dict[str, Any]:
        thread = EntropyThread(
            name,
            chaos if chaos is not None else random.uniform(0, 1),
            order if order is not None else random.uniform(0, 1),
        )
        self.threads.append(thread)
        return {"thread": thread.to_dict()}

    def weave_pair(self, idx_a: int, idx_b: int) -> Dict[str, Any]:
        if idx_a >= len(self.threads) or idx_b >= len(self.threads):
            return {"error": "thread index out of range"}
        result = self.threads[idx_a].weave_with(self.threads[idx_b])
        self.weavings.append(result)
        return result

    def perfect_balance(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self.threads if t.balance > 0.9]

    def weaver_stats(self) -> Dict[str, Any]:
        avg_beauty = sum(t.beauty for t in self.threads) / max(len(self.threads), 1)
        avg_balance = sum(t.balance for t in self.threads) / max(len(self.threads), 1)
        return {
            "total_threads": len(self.threads),
            "total_weavings": len(self.weavings),
            "avg_beauty": round(avg_beauty, 3),
            "avg_balance": round(avg_balance, 3),
        }


_weaver = EntropyWeaver()


def entropy_weaver_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "create":
        return _weaver.create_thread(
            payload.get("name", f"thread_{random.randint(100,999)}"),
            payload.get("chaos"),
            payload.get("order"),
        )
    elif action == "weave":
        return _weaver.weave_pair(payload.get("idx_a", 0), payload.get("idx_b", 1))
    elif action == "balanced":
        return {"threads": _weaver.perfect_balance()}
    return {"status": "active", **_weaver.weaver_stats()}
