"""Déjà Vu Engine — detects when the system is repeating itself.

The engine fingerprints system states and compares them to historical
states. When a current state closely matches a past state, it's flagged
as déjà vu — the system is looping. This detects hidden cycles,
recurring patterns, and temporal echoes.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class StateSnapshot:
    def __init__(self, state: Dict[str, Any]):
        self.state = state
        self.timestamp = time.time()
        self.hash = hashlib.sha256(str(sorted(state.items())).encode()).hexdigest()[:10]

    def distance(self, other: "StateSnapshot") -> float:
        all_keys = set(self.state.keys()) | set(other.state.keys())
        if not all_keys:
            return 0.0
        diffs = 0
        for key in all_keys:
            if key not in self.state or key not in other.state:
                diffs += 1
            elif self.state[key] != other.state[key]:
                diffs += 1
        return diffs / len(all_keys)


class DejaVuEngine:
    def __init__(self):
        self.snapshots: List[StateSnapshot] = []
        self.vu_events: List[Dict[str, Any]] = []
        self.cycle_count = 0

    def snapshot(self, state: Dict[str, Any]) -> Dict[str, Any]:
        snap = StateSnapshot(state)
        self.snapshots.append(snap)
        self._detect_vu(snap)
        return {"snapshotted": snap.hash, "total_snapshots": len(self.snapshots)}

    def _detect_vu(self, current: StateSnapshot):
        for past in self.snapshots[:-1]:
            distance = current.distance(past)
            if distance < 0.15:
                self.vu_events.append({
                    "current_hash": current.hash,
                    "past_hash": past.hash,
                    "distance": round(distance, 4),
                    "time_gap": round(current.timestamp - past.timestamp, 2),
                    "timestamp": current.timestamp,
                })
                if distance < 0.05:
                    self.cycle_count += 1

    def find_loops(self, threshold: float = 0.1) -> List[Dict[str, Any]]:
        loops = []
        for vu in self.vu_events:
            if vu["distance"] < threshold:
                loops.append(vu)
        return loops

    def cycle_detection(self) -> Dict[str, Any]:
        return {
            "total_deja_vu": len(self.vu_events),
            "confirmed_cycles": self.cycle_count,
            "avg_distance": round(
                sum(v["distance"] for v in self.vu_events) / max(len(self.vu_events), 1), 4
            ),
            "longest_gap": round(
                max((v["time_gap"] for v in self.vu_events), default=0), 2
            ),
        }

    def engine_stats(self) -> Dict[str, Any]:
        return {
            "total_snapshots": len(self.snapshots),
            **self.cycle_detection(),
        }


_engine = DejaVuEngine()


def deja_vu_engine_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "snapshot":
        return _engine.snapshot(payload.get("state", {}))
    elif action == "loops":
        return {"loops": _engine.find_loops(payload.get("threshold", 0.1))}
    elif action == "cycles":
        return _engine.cycle_detection()
    return {"status": "active", **_engine.engine_stats()}
