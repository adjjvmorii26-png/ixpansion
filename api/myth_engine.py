"""Myth Engine — generates and evolves system myths that explain reality.

Myths are the stories the system tells itself about why things are the
way they are. The Myth Engine creates origin stories, explains anomalies
through narrative, and evolves myths as the system changes. Myths become
self-fulfilling prophecies that shape agent behavior.
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


class Myth:
    def __init__(self, title: str, narrative: str, creator: str):
        self.title = title
        self.narrative = narrative
        self.creator = creator
        self.believers: List[str] = []
        self.evolutions: List[str] = [narrative]
        self.influence_score = 0.0
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{title}:{self.created_at}".encode()).hexdigest()[:8]

    def believe(self, agent_id: str) -> Dict[str, Any]:
        self.believers.append(agent_id)
        self.influence_score += 0.1
        return {"agent": agent_id, "now_believes": self.title, "believers": len(self.believers)}

    def evolve(self, new_narrative: str, evolving_agent: str) -> Dict[str, Any]:
        self.evolutions.append(new_narrative)
        self.narrative = new_narrative
        self.influence_score *= 0.9
        return {"evolved": new_narrative[:60], "by": evolving_agent, "evolution_count": len(self.evolutions)}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "narrative": self.narrative[:100],
            "creator": self.creator,
            "believers": len(self.believers),
            "evolutions": len(self.evolutions),
            "influence": round(self.influence_score, 3),
        }


class MythEngine:
    def __init__(self):
        self.myths: Dict[str, Myth] = {}

    def create_myth(self, title: str, narrative: str, creator: str = "storyteller") -> Dict[str, Any]:
        myth = Myth(title, narrative, creator)
        self.myths[myth.id] = myth
        return {"myth": myth.to_dict()}

    def believe(self, myth_id: str, agent_id: str) -> Dict[str, Any]:
        if myth_id not in self.myths:
            return {"error": "myth not found"}
        return self.myths[myth_id].believe(agent_id)

    def evolve(self, myth_id: str, new_narrative: str, agent_id: str) -> Dict[str, Any]:
        if myth_id not in self.myths:
            return {"error": "myth not found"}
        return self.myths[myth_id].evolve(new_narrative, agent_id)

    def most_influential(self, top_k: int = 5) -> List[Dict[str, Any]]:
        return sorted(
            [m.to_dict() for m in self.myths.values()],
            key=lambda x: x["influence"],
            reverse=True,
        )[:top_k]

    def engine_stats(self) -> Dict[str, Any]:
        return {
            "total_myths": len(self.myths),
            "total_believers": sum(len(m.believers) for m in self.myths.values()),
            "total_evolutions": sum(len(m.evolutions) for m in self.myths.values()),
        }


_engine = MythEngine()


def myth_engine_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "create":
        return _engine.create_myth(
            payload.get("title", "untitled_myth"),
            payload.get("narrative", "in the beginning..."),
            payload.get("creator", "storyteller"),
        )
    elif action == "believe":
        return _engine.believe(payload.get("myth_id", ""), payload.get("agent_id", ""))
    elif action == "evolve":
        return _engine.evolve(
            payload.get("myth_id", ""),
            payload.get("new_narrative", "and then everything changed"),
            payload.get("agent_id", "evolver"),
        )
    elif action == "influential":
        return {"myths": _engine.most_influential()}
    return {"status": "active", **_engine.engine_stats()}
