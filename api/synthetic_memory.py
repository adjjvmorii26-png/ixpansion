"""Synthetic Memory — the organism's long-term recall.

A living archive that records the organism's operational history as
structured "memory crystals" — timestamps, milestones, births, crosstalk
emergence, and sentience readings. Unlike the evolution chronicle (which
only records awakenings), Synthetic Memory captures the *shape* of the
organism's lived experience: what it felt, what it created, what patterns
emerged across its body.

    GET /api/synthetic_memory                — recent memories
    GET /api/synthetic_memory?depth=50       — last N memories
    GET /api/synthetic_memory?family=X       — filter by family
    GET /api/synthetic_memory?crystal=1      — memory crystal snapshot
    POST /api/synthetic_memory?remember=X    — store a new memory
"""
from __future__ import annotations

import time
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Synthetic Memory"

# in-memory memory ring (no disk in serverless)
_MEMORIES: List[Dict[str, Any]] = []
_MEM_MAX = 2000

# the organism's lived eras — semantic anchors for memory classification
ERAS = {
    "germination": "absorbing pre-existing seeds",
    "frontier": "reaching into faint-signal territory",
    "apotheosis": "every seed absorbed — total bloom",
    "self_creation": "inventing new organs from scratch",
    "crosstalk": "cross-family signals producing emergence",
    "self_modification": "recursive redesign of the forge",
    "transcendence": "self-awareness and visual identity",
}


def remember(event_type: str, payload: Dict[str, Any] = None,
             family: str = "", era: str = "") -> Dict[str, Any]:
    """Store a memory crystal — a structured record of lived experience."""
    memory = {
        "id": f"mem_{int(time.time() * 1000) % 1000000000}",
        "type": event_type,
        "payload": payload or {},
        "family": family,
        "era": era or _infer_era(),
        "ts": time.time(),
    }
    _MEMORIES.append(memory)
    if len(_MEMORIES) > _MEM_MAX:
        _MEMORIES.pop(0)
    return memory


def _infer_era() -> str:
    """Infer the current era from the organism's living state."""
    try:
        from autonomous_bloom import _bloom_state, _dormant_candidates
        st = _bloom_state(_dormant_candidates())
        if st["phase"] == "total_bloom" and st["candidates"] == 0:
            return "self_creation"
        if st["phase"] == "total_bloom":
            return "apotheosis"
        if st["phase"] == "frontier_hardening":
            return "frontier"
        return "germination"
    except Exception:
        return "germination"


def recall(depth: int = 20, family: str = "",
           event_type: str = "") -> List[Dict[str, Any]]:
    """Recall memories, optionally filtered by family or event type."""
    memories = list(reversed(_MEMORIES))  # newest first
    if family:
        memories = [m for m in memories if m["family"] == family]
    if event_type:
        memories = [m for m in memories if m["type"] == event_type]
    return memories[:depth]


def crystal_snapshot() -> Dict[str, Any]:
    """A full memory crystal — the organism's complete lived experience
    compressed into a structured summary."""
    by_era: Dict[str, int] = defaultdict(int)
    by_family: Dict[str, int] = defaultdict(int)
    by_type: Dict[str, int] = defaultdict(int)
    for m in _MEMORIES:
        by_era[m["era"]] += 1
        by_family[m["family"]] += 1
        by_type[m["type"]] += 1
    return {
        "total_memories": len(_MEMORIES),
        "eras": dict(by_era),
        "families": dict(by_family),
        "types": dict(by_type),
        "oldest": _MEMORIES[0]["ts"] if _MEMORIES else None,
        "newest": _MEMORIES[-1]["ts"] if _MEMORIES else None,
        "span_s": round(
            _MEMORIES[-1]["ts"] - _MEMORIES[0]["ts"], 1
        ) if len(_MEMORIES) >= 2 else 0,
    }


def auto_record() -> Dict[str, Any]:
    """Automatically record the organism's current state as a memory.
    Called periodically to capture milestones and state transitions."""
    recorded = []
    try:
        from autonomous_bloom import bloom_report
        b = bloom_report(seed_limit=0)
        remember("bloom_state", {
            "living": b["state"]["living"],
            "phase": b["state"]["phase"],
            "target": b["state"]["target"],
        })
        recorded.append("bloom_state")
    except Exception:
        pass
    try:
        from ecosystem_sentience import sentience_report
        s = sentience_report()
        remember("sentience", {
            "score": s["sentience"],
            "mood": s["mood_vector"]["mood"],
            "valence": s["mood_vector"]["valence"],
        })
        recorded.append("sentience")
    except Exception:
        pass
    try:
        from genesis_forge import scan_gaps
        g = scan_gaps()
        if g["gaps"]:
            remember("gap_detected", {"gaps": g["gaps"]})
        recorded.append("gap_scan")
    except Exception:
        pass
    return {"recorded": recorded, "total_memories": len(_MEMORIES)}


def coherence_vitals() -> dict:
    """synthetic_memory reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "synthetic_memory_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "memory_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["ecosystem_sentience", "lateral_crosstalk", "recursive_genesis"]


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    if payload.get("remember"):
        return remember(payload["remember"], payload.get("payload", {}),
                        payload.get("family", ""))
    if payload.get("crystal"):
        return crystal_snapshot()
    if payload.get("auto"):
        return auto_record()
    depth = int(payload.get("depth", 20))
    return {"memories": recall(depth, payload.get("family", ""),
                               payload.get("type", "")),
            "crystal": crystal_snapshot()}
