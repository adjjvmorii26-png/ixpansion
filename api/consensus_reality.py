"""Consensus Reality — observers collapse possibility into shared existence.

Nothing exists until enough agents agree it does. This module manages
the consensus process: agents propose entities, vote on their reality,
and the system collapses possibilities based on collective agreement.
The more agents believe, the more real something becomes.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class ProposedEntity:
    def __init__(self, name: str, description: str, proposer: str):
        self.name = name
        self.description = description
        self.proposer = proposer
        self.votes: Dict[str, bool] = {}
        self.reality_score = 0.0
        self.exists = False
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{name}:{proposer}".encode()).hexdigest()[:10]
        self.attributes: Dict[str, Any] = {}

    def vote(self, agent_id: str, believes: bool) -> Dict[str, Any]:
        self.votes[agent_id] = believes
        self._update_reality()
        return {
            "entity": self.name,
            "voter": agent_id,
            "believes": believes,
            "reality_score": round(self.reality_score, 4),
            "exists": self.exists,
        }

    def _update_reality(self):
        if not self.votes:
            self.reality_score = 0.0
            self.exists = False
            return
        believers = sum(1 for v in self.votes.values() if v)
        total = len(self.votes)
        self.reality_score = believers / total
        self.exists = self.reality_score >= 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description[:100],
            "proposer": self.proposer,
            "reality_score": round(self.reality_score, 4),
            "exists": self.exists,
            "votes": len(self.votes),
            "believers": sum(1 for v in self.votes.values() if v),
            "age_seconds": time.time() - self.timestamp,
        }


class ConsensusReality:
    def __init__(self):
        self.entities: Dict[str, ProposedEntity] = {}
        self.collapse_events: List[Dict[str, Any]] = []
        self.total_votes = 0

    def propose(self, name: str, description: str, proposer: str) -> Dict[str, Any]:
        entity = ProposedEntity(name, description, proposer)
        self.entities[entity.id] = entity
        return {"proposed": entity.to_dict()}

    def vote(self, entity_id: str, agent_id: str, believes: bool) -> Dict[str, Any]:
        if entity_id not in self.entities:
            return {"error": "entity not found"}
        entity = self.entities[entity_id]
        was_real = entity.exists
        result = entity.vote(agent_id, believes)
        self.total_votes += 1
        if not was_real and entity.exists:
            self.collapse_events.append({
                "entity": entity.name,
                "event": "collapsed_into_existence",
                "believers": sum(1 for v in entity.votes.values() if v),
                "total_voters": len(entity.votes),
                "time": time.time(),
            })
            result["event"] = "JUST_CAME_INTO_EXISTENCE"
        elif was_real and not entity.exists:
            self.collapse_events.append({
                "entity": entity.name,
                "event": "dissolved_from_reality",
                "time": time.time(),
            })
            result["event"] = "JUST_CEASED_TO_EXIST"
        return result

    def get_real_entities(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self.entities.values() if e.exists]

    def get_void_entities(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self.entities.values() if not e.exists]

    def entity_detail(self, entity_id: str) -> Optional[Dict[str, Any]]:
        if entity_id not in self.entities:
            return None
        entity = self.entities[entity_id]
        return {
            **entity.to_dict(),
            "voters": {k: v for k, v in entity.votes.items()},
        }

    def reality_stats(self) -> Dict[str, Any]:
        real = sum(1 for e in self.entities.values() if e.exists)
        void = len(self.entities) - real
        return {
            "total_entities": len(self.entities),
            "real": real,
            "void": void,
            "total_votes": self.total_votes,
            "collapse_events": len(self.collapse_events),
            "avg_reality_score": round(
                sum(e.reality_score for e in self.entities.values()) /
                max(len(self.entities), 1), 4
            ),
        }


_reality = ConsensusReality()


def consensus_reality_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "propose":
        return _reality.propose(
            payload.get("name", "unnamed_thing"),
            payload.get("description", "something that might exist"),
            payload.get("proposer", "observer"),
        )
    elif action == "vote":
        return _reality.vote(
            payload.get("entity_id", ""),
            payload.get("agent_id", "voter"),
            payload.get("believes", True),
        )
    elif action == "real":
        return {"entities": _reality.get_real_entities()}
    elif action == "void":
        return {"entities": _reality.get_void_entities()}
    elif action == "detail":
        detail = _reality.entity_detail(payload.get("entity_id", ""))
        return detail or {"error": "entity not found"}
    return {"status": "active", **_reality.reality_stats()}


handler = consensus_reality_handler
