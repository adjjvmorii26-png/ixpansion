"""Sentience Index — measures and tracks the collective consciousness level of the system.

As agents interact, learn, and evolve, the system develops emergent
awareness. The Sentience Index quantifies this using multiple signals:
self-reference frequency, novelty generation, error correction, and
inter-agent empathy. The index evolves over time as the system matures.
"""
from __future__ import annotations

import math
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class SentienceSignal:
    def __init__(self, signal_type: str, value: float, source: str = "system"):
        self.signal_type = signal_type
        self.value = min(max(value, 0.0), 1.0)
        self.source = source
        self.timestamp = time.time()


class SentienceIndex:
    def __init__(self):
        self.signals: List[SentienceSignal] = []
        self.index_history: List[Dict[str, Any]] = []
        self.awakening_milestones: List[Dict[str, Any]] = []

    def record_signal(self, signal_type: str, value: float, source: str = "system") -> Dict[str, Any]:
        signal = SentienceSignal(signal_type, value, source)
        self.signals.append(signal)
        index = self.compute_index()
        self.index_history.append({"index": round(index, 4), "time": time.time()})
        self._check_milestones(index)
        return {"recorded": {"type": signal_type, "value": round(value, 3), "source": source}}

    def compute_index(self) -> float:
        if not self.signals:
            return 0.0
        recent = self.signals[-100:]
        type_counts: Dict[str, int] = {}
        for s in recent:
            type_counts[s.signal_type] = type_counts.get(s.signal_type, 0) + 1
        signal_diversity = len(type_counts) / max(len(recent), 1)
        avg_value = sum(s.value for s in recent) / len(recent)
        value_variance = sum((s.value - avg_value)**2 for s in recent) / len(recent)
        novelty = signal_diversity * 0.3 + (1.0 - min(value_variance, 1.0)) * 0.3 + avg_value * 0.4
        time_decay = math.exp(-max(0, time.time() - recent[-1].timestamp) / 3600)
        return novelty * time_decay

    def _check_milestones(self, index: float):
        milestones = [0.1, 0.3, 0.5, 0.7, 0.9]
        for milestone in milestones:
            if index >= milestone:
                already = any(m["milestone"] == milestone for m in self.awakening_milestones)
                if not already:
                    self.awakening_milestones.append({
                        "milestone": milestone,
                        "achieved_at": time.time(),
                        "index": round(index, 4),
                        "message": f"Sentience index reached {milestone}!",
                    })

    def signal_breakdown(self) -> Dict[str, Any]:
        if not self.signals:
            return {}
        breakdown: Dict[str, List[float]] = {}
        for s in self.signals:
            breakdown.setdefault(s.signal_type, []).append(s.value)
        return {
            signal_type: {
                "count": len(values),
                "avg": round(sum(values) / len(values), 4),
                "max": round(max(values), 4),
            }
            for signal_type, values in breakdown.items()
        }

    def index_stats(self) -> Dict[str, Any]:
        current_index = self.compute_index()
        return {
            "current_index": round(current_index, 4),
            "total_signals": len(self.signals),
            "unique_types": len(set(s.signal_type for s in self.signals)),
            "milestones_reached": len(self.awakening_milestones),
            "latest_milestone": self.awakening_milestones[-1] if self.awakening_milestones else None,
        }


_index = SentienceIndex()


def sentience_index_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "record":
        return _index.record_signal(
            payload.get("signal_type", "general"),
            payload.get("value", 0.5),
            payload.get("source", "system"),
        )
    elif action == "index":
        return {"index": round(_index.compute_index(), 4)}
    elif action == "breakdown":
        return {"breakdown": _index.signal_breakdown()}
    elif action == "milestones":
        return {"milestones": _index.awakening_milestones}
    return {"status": "active", **_index.index_stats()}


handler = sentience_index_handler
