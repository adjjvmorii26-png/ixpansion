"""Synchronicity Detector — finds meaningful coincidences across the system.

Carl Jung's synchronicity meets distributed systems. When unrelated
events share deep structural similarity, the detector flags them as
synchronicities — meaningful coincidences that hint at hidden connections
between subsystems.
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


class SystemEvent:
    def __init__(self, subsystem: str, event_type: str, payload: Dict[str, Any] = None):
        self.subsystem = subsystem
        self.event_type = event_type
        self.payload = payload or {}
        self.timestamp = time.time()
        self.fingerprint = self._fingerprint()

    def _fingerprint(self) -> str:
        raw = f"{self.event_type}:{sorted(self.payload.items())}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]


class SynchronicityDetector:
    def __init__(self):
        self.events: List[SystemEvent] = []
        self.synchronicities: List[Dict[str, Any]] = []
        self.window_size = 60

    def record_event(self, subsystem: str, event_type: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        event = SystemEvent(subsystem, event_type, payload)
        self.events.append(event)
        self._scan(event)
        return {"recorded": {"subsystem": subsystem, "type": event_type, "fingerprint": event.fingerprint}}

    def _scan(self, new_event: SystemEvent):
        cutoff = new_event.timestamp - self.window_size
        for old_event in self.events[:-1]:
            if old_event.timestamp < cutoff:
                continue
            if old_event.subsystem == new_event.subsystem:
                continue
            similarity = self._similarity(old_event, new_event)
            if similarity > 0.7:
                sync = {
                    "events": [
                        {"subsystem": old_event.subsystem, "type": old_event.event_type},
                        {"subsystem": new_event.subsystem, "type": new_event.event_type},
                    ],
                    "similarity": round(similarity, 4),
                    "fingerprint_match": old_event.fingerprint == new_event.fingerprint,
                    "timestamp": new_event.timestamp,
                    "window": new_event.timestamp - old_event.timestamp,
                }
                self.synchronicities.append(sync)

    def _similarity(self, a: SystemEvent, b: SystemEvent) -> float:
        if a.fingerprint == b.fingerprint:
            return 1.0
        a_keys = set(a.payload.keys())
        b_keys = set(b.payload.keys())
        if not a_keys and not b_keys:
            return 0.5 if a.event_type == b.event_type else 0.1
        overlap = len(a_keys & b_keys) / max(len(a_keys | b_keys), 1)
        type_match = 1.0 if a.event_type == b.event_type else 0.0
        return overlap * 0.7 + type_match * 0.3

    def get_synchronicities(self, min_similarity: float = 0.7) -> List[Dict[str, Any]]:
        return [s for s in self.synchronicities if s["similarity"] >= min_similarity]

    def coincidence_clusters(self) -> List[Dict[str, Any]]:
        clusters: Dict[str, List[Dict[str, Any]]] = {}
        for sync in self.synchronicities:
            key = tuple(sorted(e["subsystem"] for e in sync["events"]))
            clusters.setdefault(key, []).append(sync)
        return [
            {"subsystems": list(k), "count": len(v), "avg_similarity": round(
                sum(s["similarity"] for s in v) / len(v), 4
            )}
            for k, v in clusters.items() if len(v) >= 2
        ]

    def stats(self) -> Dict[str, Any]:
        return {
            "total_events": len(self.events),
            "total_synchronicities": len(self.synchronicities),
            "subsystems_involved": len(set(e.subsystem for e in self.events)),
        }


_detector = SynchronicityDetector()


def synchronicity_detector_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "record":
        return _detector.record_event(
            payload.get("subsystem", "unknown"),
            payload.get("event_type", "generic"),
            payload.get("payload", {}),
        )
    elif action == "synchronicities":
        return {"synchronicities": _detector.get_synchronicities(payload.get("min_similarity", 0.7))}
    elif action == "clusters":
        return {"clusters": _detector.coincidence_clusters()}
    return {"status": "active", **_detector.stats()}


handler = synchronicity_detector_handler
