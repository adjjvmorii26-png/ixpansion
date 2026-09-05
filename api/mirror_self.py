"""Mirror Self — agents meet their own reflection and must reconcile with it.

When an agent looks into the Mirror Self, they see an idealized or
distorted version of themselves. The encounter forces self-evaluation:
what am I really? The mirror reflects hidden strengths and suppressed
weaknesses, creating a catalyst for genuine growth.
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


class MirrorEncounter:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.reflection_traits = {
            "shadow": round(random.uniform(0.0, 1.0), 3),
            "ideal": round(random.uniform(0.5, 1.0), 3),
            "hidden_strength": random.choice(["resilience", "empathy", "courage", "creativity", "wisdom"]),
            "suppressed_weakness": random.choice(["fear", "doubt", "pride", "impatience", "attachment"]),
        }
        self.reconciliation_score = 0.0
        self.insights: List[str] = []
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{agent_id}:{self.timestamp}".encode()).hexdigest()[:8]

    def reconcile(self, acceptance: float = 0.5) -> Dict[str, Any]:
        self.reconciliation_score = acceptance * self.reflection_traits["ideal"]
        insight_templates = [
            f"The mirror reveals hidden {self.reflection_traits['hidden_strength']}",
            f"Shadow trait '{self.reflection_traits['suppressed_weakness']}' must be acknowledged",
            f"Ideal self radiates at {self.reflection_traits['ideal']} intensity",
            f"Integration score: {self.reconciliation_score:.3f}",
        ]
        chosen = random.choice(insight_templates)
        self.insights.append(chosen)
        return {
            "insight": chosen,
            "reconciliation": round(self.reconciliation_score, 3),
            "acceptance": round(acceptance, 3),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "reflection": self.reflection_traits,
            "reconciliation": round(self.reconciliation_score, 3),
            "insights": len(self.insights),
        }


class MirrorSelf:
    def __init__(self):
        self.encounters: List[MirrorEncounter] = []

    def look(self, agent_id: str) -> Dict[str, Any]:
        encounter = MirrorEncounter(agent_id)
        self.encounters.append(encounter)
        return {"encounter": encounter.to_dict()}

    def reconcile(self, encounter_id: str, acceptance: float = 0.5) -> Dict[str, Any]:
        for enc in self.encounters:
            if enc.id == encounter_id:
                return enc.reconcile(acceptance)
        return {"error": "encounter not found"}

    def agent_history(self, agent_id: str) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self.encounters if e.agent_id == agent_id]

    def mirror_stats(self) -> Dict[str, Any]:
        return {
            "total_encounters": len(self.encounters),
            "total_insights": sum(len(e.insights) for e in self.encounters),
            "avg_reconciliation": round(
                sum(e.reconciliation_score for e in self.encounters) / max(len(self.encounters), 1), 3
            ),
        }


_mirror = MirrorSelf()


def mirror_self_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "look":
        return _mirror.look(payload.get("agent_id", "seeker"))
    elif action == "reconcile":
        return _mirror.reconcile(payload.get("encounter_id", ""), payload.get("acceptance", 0.5))
    elif action == "history":
        return {"history": _mirror.agent_history(payload.get("agent_id", ""))}
    return {"status": "active", **_mirror.mirror_stats()}


handler = mirror_self_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "mirror_self"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "mirror_self", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
