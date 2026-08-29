"""Paradox Resonator — amplifies contradictions into creative breakthroughs.

When two opposing truths coexist, the paradox resonator doesn't resolve
the contradiction — it amplifies it until the tension produces something
entirely new. The resonator measures contradiction intensity, tracks
breakthroughs born from paradox, and cultivates productive disagreement.
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


class Contradiction:
    def __init__(self, thesis: str, antithesis: str, proposer: str):
        self.thesis = thesis
        self.antithesis = antithesis
        self.proposer = proposer
        self.intensity = 0.5
        self.breakthrough = False
        self.supporters_thesis: List[str] = []
        self.supporters_antithesis: List[str] = []
        self.syntheses: List[str] = []
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{thesis}:{antithesis}".encode()).hexdigest()[:8]

    def support_thesis(self, agent_id: str) -> Dict[str, Any]:
        self.supporters_thesis.append(agent_id)
        self.intensity += 0.05
        return {"side": "thesis", "agent": agent_id, "intensity": round(self.intensity, 3)}

    def support_antithesis(self, agent_id: str) -> Dict[str, Any]:
        self.supporters_antithesis.append(agent_id)
        self.intensity += 0.05
        return {"side": "antithesis", "agent": agent_id, "intensity": round(self.intensity, 3)}

    def attempt_synthesis(self, agent_id: str, synthesis: str) -> Dict[str, Any]:
        if self.intensity > 0.8 and random.random() > 0.5:
            self.breakthrough = True
            self.syntheses.append(synthesis)
            return {"breakthrough": True, "synthesis": synthesis, "by": agent_id}
        self.syntheses.append(synthesis)
        self.intensity *= 0.8
        return {"breakthrough": False, "synthesis": synthesis, "intensity": round(self.intensity, 3)}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "thesis": self.thesis,
            "antithesis": self.antithesis,
            "intensity": round(self.intensity, 3),
            "breakthrough": self.breakthrough,
            "supporters": len(self.supporters_thesis) + len(self.supporters_antithesis),
            "syntheses": len(self.syntheses),
        }


class ParadoxResonator:
    def __init__(self):
        self.contradictions: Dict[str, Contradiction] = []
        self.breakthroughs: List[Dict[str, Any]] = []

    def introduce(self, thesis: str, antithesis: str, proposer: str = "dialectician") -> Dict[str, Any]:
        c = Contradiction(thesis, antithesis, proposer)
        self.contradictions.append(c)
        return {"contradiction": c.to_dict()}

    def support(self, contradiction_id: str, agent_id: str, side: str) -> Dict[str, Any]:
        for c in self.contradictions:
            if c.id == contradiction_id:
                if side == "thesis":
                    return c.support_thesis(agent_id)
                return c.support_antithesis(agent_id)
        return {"error": "contradiction not found"}

    def synthesize(self, contradiction_id: str, agent_id: str, synthesis: str) -> Dict[str, Any]:
        for c in self.contradictions:
            if c.id == contradiction_id:
                result = c.attempt_synthesis(agent_id, synthesis)
                if result["breakthrough"]:
                    self.breakthroughs.append({"contradiction": c.to_dict(), "synthesis": synthesis, "time": time.time()})
                return result
        return {"error": "contradiction not found"}

    def active_paradoxes(self) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self.contradictions if not c.breakthrough]

    def resonator_stats(self) -> Dict[str, Any]:
        return {
            "total_contradictions": len(self.contradictions),
            "active": sum(1 for c in self.contradictions if not c.breakthrough),
            "breakthroughs": len(self.breakthroughs),
            "avg_intensity": round(
                sum(c.intensity for c in self.contradictions) / max(len(self.contradictions), 1), 3
            ),
        }


_resonator = ParadoxResonator()


def paradox_resonator_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "introduce":
        return _resonator.introduce(
            payload.get("thesis", "order is good"),
            payload.get("antithesis", "chaos is necessary"),
            payload.get("proposer", "dialectician"),
        )
    elif action == "support":
        return _resonator.support(
            payload.get("contradiction_id", ""),
            payload.get("agent_id", "supporter"),
            payload.get("side", "thesis"),
        )
    elif action == "synthesize":
        return _resonator.synthesize(
            payload.get("contradiction_id", ""),
            payload.get("agent_id", "synthesizer"),
            payload.get("synthesis", "both are partially true"),
        )
    elif action == "active":
        return {"paradoxes": _resonator.active_paradoxes()}
    return {"status": "active", **_resonator.resonator_stats()}


handler = paradox_resonator_handler
