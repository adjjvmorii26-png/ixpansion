"""Shadow Ledger — records everything that DIDN'T happen.

For every action taken, a shadow entry records what was considered
but rejected, what could have been, and the paths not taken. This
counterfactual history reveals hidden patterns in decision-making.
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


class ShadowEntry:
    def __init__(self, action_taken: str, alternatives_rejected: List[str], context: Dict[str, Any] = None):
        self.action_taken = action_taken
        self.alternatives_rejected = alternatives_rejected
        self.context = context or {}
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{action_taken}:{self.timestamp}".encode()).hexdigest()[:10]
        self.regret_score = random.uniform(0.0, 1.0)
        self.alternative_quality = [random.uniform(0.3, 1.0) for _ in alternatives_rejected]

    def to_dict(self) -> Dict[str, Any]:
        best_alternative = ""
        best_score = 0.0
        for i, alt in enumerate(self.alternatives_rejected):
            if self.alternative_quality[i] > best_score:
                best_score = self.alternative_quality[i]
                best_alternative = alt
        return {
            "id": self.id,
            "action_taken": self.action_taken,
            "alternatives_rejected": self.alternatives_rejected,
            "regret_score": round(self.regret_score, 4),
            "best_rejected": best_alternative,
            "best_rejected_quality": round(best_score, 4),
            "timestamp": self.timestamp,
        }


class ShadowLedger:
    def __init__(self):
        self.entries: List[ShadowEntry] = []
        self.regret_patterns: Dict[str, int] = {}

    def record(self, action_taken: str, alternatives: List[str], context: Dict[str, Any] = None) -> Dict[str, Any]:
        entry = ShadowEntry(action_taken, alternatives, context)
        self.entries.append(entry)
        for alt in alternatives:
            self.regret_patterns[alt] = self.regret_patterns.get(alt, 0) + 1
        return {"recorded": entry.to_dict()}

    def analyze_regret(self, last_n: int = 10) -> Dict[str, Any]:
        recent = self.entries[-last_n:] if len(self.entries) >= last_n else self.entries
        if not recent:
            return {"message": "no shadow entries yet"}
        avg_regret = sum(e.regret_score for e in recent) / len(recent)
        avg_alternative_quality = sum(
            max(e.alternative_quality) if e.alternative_quality else 0 for e in recent
        ) / len(recent)
        return {
            "entries_analyzed": len(recent),
            "average_regret": round(avg_regret, 4),
            "average_best_alternative_quality": round(avg_alternative_quality, 4),
            "missed_opportunities": sum(1 for e in recent if e.regret_score > 0.7),
        }

    def find_counterfactual(self, action: str) -> List[Dict[str, Any]]:
        """Find all shadows where a specific action was rejected."""
        shadows = []
        for entry in self.entries:
            if action in entry.alternatives_rejected:
                idx = entry.alternatives_rejected.index(action)
                shadows.append({
                    "rejected_in_favor_of": entry.action_taken,
                    "quality_of_rejected": round(entry.alternative_quality[idx], 4),
                    "timestamp": entry.timestamp,
                })
        return shadows

    def most_rejected(self, top_k: int = 5) -> List[Dict[str, Any]]:
        sorted_patterns = sorted(self.regret_patterns.items(), key=lambda x: x[1], reverse=True)
        return [{"action": action, "rejection_count": count} for action, count in sorted_patterns[:top_k]]

    def stats(self) -> Dict[str, Any]:
        return {
            "total_shadow_entries": len(self.entries),
            "unique_rejected_actions": len(self.regret_patterns),
            "avg_regret": round(
                sum(e.regret_score for e in self.entries) / max(len(self.entries), 1), 4
            ),
        }


_ledger = ShadowLedger()


def shadow_ledger_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "record":
        return _ledger.record(
            payload.get("action_taken", "default_action"),
            payload.get("alternatives", ["alt_1", "alt_2"]),
            payload.get("context"),
        )
    elif action == "regret":
        return _ledger.analyze_regret(payload.get("last_n", 10))
    elif action == "counterfactual":
        return {"shadows": _ledger.find_counterfactual(payload.get("action", ""))}
    elif action == "most_rejected":
        return {"most_rejected": _ledger.most_rejected(payload.get("top_k", 5))}
    return {"status": "active", **_ledger.stats()}


handler = shadow_ledger_handler
