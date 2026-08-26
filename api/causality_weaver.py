"""Causality Weaver — spin cause-and-effect threads between events.

Events are not just logged — they're woven into a causal tapestry.
The weaver identifies which events caused others, creates causal
chains, and detects circular causality (causal loops).
"""
from __future__ import annotations

import hashlib
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class CausalEvent:
    def __init__(self, name: str, data: Any = None):
        self.name = name
        self.data = data or {}
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{name}:{self.timestamp}".encode()).hexdigest()[:10]

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "data": self.data, "timestamp": self.timestamp}


class CausalThread:
    def __init__(self, cause_id: str, effect_id: str, strength: float = 1.0):
        self.cause_id = cause_id
        self.effect_id = effect_id
        self.strength = min(max(strength, 0.0), 1.0)
        self.timestamp = time.time()


class CausalityWeaver:
    def __init__(self):
        self.events: Dict[str, CausalEvent] = {}
        self.threads: List[CausalThread] = []
        self.loops: List[List[str]] = []

    def weave_event(self, name: str, data: Any = None) -> str:
        event = CausalEvent(name, data)
        self.events[event.id] = event
        return event.id

    def weave_cause(self, cause_id: str, effect_id: str, strength: float = 1.0) -> Dict[str, Any]:
        if cause_id not in self.events or effect_id not in self.events:
            return {"error": "event not found"}
        thread = CausalThread(cause_id, effect_id, strength)
        self.threads.append(thread)
        loop = self._detect_loop(effect_id, cause_id)
        if loop:
            self.loops.append(loop)
            return {
                "woven": True,
                "loop_detected": True,
                "loop": loop,
                "strength": strength,
            }
        return {"woven": True, "loop_detected": False, "strength": strength}

    def _detect_loop(self, from_id: str, to_id: str) -> Optional[List[str]]:
        visited: Set[str] = set()
        path = [from_id]
        queue = [from_id]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            for thread in self.threads:
                if thread.cause_id == current:
                    next_id = thread.effect_id
                    if next_id == to_id:
                        return path + [next_id]
                    queue.append(next_id)
                    path.append(next_id)
        return None

    def trace_causes(self, event_id: str, depth: int = 5) -> List[Dict[str, Any]]:
        causes = []
        visited: Set[str] = set()
        queue = [(event_id, 0)]
        while queue:
            eid, d = queue.pop(0)
            if eid in visited or d > depth:
                continue
            visited.add(eid)
            for thread in self.threads:
                if thread.effect_id == eid:
                    cause_event = self.events.get(thread.cause_id)
                    if cause_event:
                        causes.append({
                            "event": cause_event.to_dict(),
                            "strength": thread.strength,
                            "depth": d + 1,
                        })
                        queue.append((thread.cause_id, d + 1))
        return causes

    def trace_effects(self, event_id: str, depth: int = 5) -> List[Dict[str, Any]]:
        effects = []
        visited: Set[str] = set()
        queue = [(event_id, 0)]
        while queue:
            eid, d = queue.pop(0)
            if eid in visited or d > depth:
                continue
            visited.add(eid)
            for thread in self.threads:
                if thread.cause_id == eid:
                    effect_event = self.events.get(thread.effect_id)
                    if effect_event:
                        effects.append({
                            "event": effect_event.to_dict(),
                            "strength": thread.strength,
                            "depth": d + 1,
                        })
                        queue.append((thread.effect_id, d + 1))
        return effects

    def tapestry_stats(self) -> Dict[str, Any]:
        return {
            "total_events": len(self.events),
            "total_threads": len(self.threads),
            "causal_loops": len(self.loops),
            "avg_thread_strength": round(
                sum(t.strength for t in self.threads) / max(len(self.threads), 1), 3
            ),
        }


_weaver = CausalityWeaver()


def causality_weaver_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "event":
        eid = _weaver.weave_event(payload.get("name", "event"), payload.get("data"))
        return {"event_id": eid, "name": payload.get("name")}
    elif action == "cause":
        return _weaver.weave_cause(
            payload.get("cause_id", ""), payload.get("effect_id", ""),
            payload.get("strength", 1.0),
        )
    elif action == "trace_causes":
        return {"causes": _weaver.trace_causes(payload.get("event_id", ""), payload.get("depth", 5))}
    elif action == "trace_effects":
        return {"effects": _weaver.trace_effects(payload.get("event_id", ""), payload.get("depth", 5))}
    elif action == "loops":
        return {"loops": _weaver.loops}
    return {"status": "active", **_weaver.tapestry_stats()}
