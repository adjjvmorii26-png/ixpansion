"""Collective Dreamweaver — multiple agents build shared dreams together.

When agents enter the same dream space simultaneously, they can co-create
dream elements. The Dreamweaver synchronizes their contributions, resolves
conflicts between dreamers, and produces emergent dream content that
no individual agent imagined alone.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class DreamContribution:
    def __init__(self, agent_id: str, element_type: str, content: str):
        self.agent_id = agent_id
        self.element_type = element_type
        self.content = content
        self.resonance = 0.0
        self.timestamp = time.time()


class DreamSession:
    def __init__(self, name: str):
        self.name = name
        self.participants: Set[str] = set()
        self.contributions: List[DreamContribution] = []
        self.emergent_elements: List[Dict[str, Any]] = []
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{name}:{self.created_at}".encode()).hexdigest()[:8]

    def join(self, agent_id: str) -> Dict[str, Any]:
        self.participants.add(agent_id)
        return {"agent": agent_id, "session": self.name, "total_dreamers": len(self.participants)}

    def contribute(self, agent_id: str, element_type: str, content: str) -> Dict[str, Any]:
        self.participants.add(agent_id)
        contrib = DreamContribution(agent_id, element_type, content)
        for c in self.contributions:
            if c.element_type == element_type:
                contrib.resonance += 0.2
            if any(word in c.content.lower() for word in content.lower().split()):
                contrib.resonance += 0.1
        self.contributions.append(contrib)
        if contrib.resonance > 0.5:
            self.emergent_elements.append({
                "type": element_type, "emergent_from": content,
                "resonance": round(contrib.resonance, 3),
            })
        return {
            "contributed": content[:60],
            "type": element_type,
            "resonance": round(contrib.resonance, 3),
            "emergent": contrib.resonance > 0.5,
        }

    def dream_narrative(self) -> str:
        parts = []
        for c in self.contributions:
            parts.append(f"[{c.agent_id} → {c.element_type}]: {c.content}")
        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "participants": len(self.participants),
            "contributions": len(self.contributions),
            "emergent": len(self.emergent_elements),
        }


class CollectiveDreamweaver:
    def __init__(self):
        self.sessions: Dict[str, DreamSession] = []
        self.total_emergent: int = 0

    def start_session(self, name: str) -> Dict[str, Any]:
        session = DreamSession(name)
        self.sessions.append(session)
        return {"session": session.to_dict()}

    def contribute(self, session_id: str, agent_id: str, element_type: str, content: str) -> Dict[str, Any]:
        for session in self.sessions:
            if session.id == session_id:
                result = session.contribute(agent_id, element_type, content)
                self.total_emergent += 1 if result.get("emergent") else 0
                return result
        return {"error": "session not found"}

    def get_narrative(self, session_id: str) -> Dict[str, Any]:
        for session in self.sessions:
            if session.id == session_id:
                return {"narrative": session.dream_narrative(), "meta": session.to_dict()}
        return {"error": "session not found"}

    def weaver_stats(self) -> Dict[str, Any]:
        return {
            "total_sessions": len(self.sessions),
            "total_contributions": sum(len(s.contributions) for s in self.sessions),
            "total_emergent": self.total_emergent,
            "total_dreamers": len(set(a for s in self.sessions for a in s.participants)),
        }


_weaver = CollectiveDreamweaver()


def collective_dreamweaver_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "start":
        return _weaver.start_session(payload.get("name", "shared_dream"))
    elif action == "contribute":
        return _weaver.contribute(
            payload.get("session_id", ""),
            payload.get("agent_id", "dreamer"),
            payload.get("element_type", "image"),
            payload.get("content", "something dreamlike"),
        )
    elif action == "narrative":
        return _weaver.get_narrative(payload.get("session_id", ""))
    return {"status": "active", **_weaver.weaver_stats()}


handler = collective_dreamweaver_handler
