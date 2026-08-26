"""Legacy Weaver — threads the stories of retired agents into the system's mythos.

When agents retire, their complete journey — triumphs, failures, and
transformations — gets woven into the system's living mythology. The
Legacy Weaver creates archetypal narratives that guide future agents
and preserve institutional memory in story form.
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


class LegacyThread:
    def __init__(self, agent_id: str, journey: List[str], outcome: str):
        self.agent_id = agent_id
        self.journey = journey
        self.outcome = outcome
        self.archetype = self._determine_archetype()
        self.woven_at = time.time()
        self.id = hashlib.sha256(f"{agent_id}:{self.woven_at}".encode()).hexdigest()[:8]
        self.influences: List[str] = []

    def _determine_archetype(self) -> str:
        archetypes = {
            "triumph": "the hero",
            "sacrifice": "the martyr",
            "discovery": "the explorer",
            "transformation": "the shapeshifter",
            "endurance": "the survivor",
            "innovation": "the creator",
            "wisdom": "the sage",
            "mystery": "the enigma",
        }
        return archetypes.get(self.outcome, "the wanderer")

    def influence(self, agent_id: str) -> Dict[str, Any]:
        self.influences.append(agent_id)
        return {
            "influenced": agent_id,
            "archetype": self.archetype,
            "lesson": f"From {self.agent_id}'s journey as {self.archetype}: the path is rarely straight.",
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "archetype": self.archetype,
            "journey_length": len(self.journey),
            "outcome": self.outcome,
            "influences": len(self.influences),
        }


class LegacyWeaver:
    def __init__(self):
        self.threads: List[LegacyThread] = []
        self.mythology: List[Dict[str, Any]] = []

    def weave(self, agent_id: str, journey: List[str], outcome: str) -> Dict[str, Any]:
        thread = LegacyThread(agent_id, journey, outcome)
        self.threads.append(thread)
        self.mythology.append({
            "archetype": thread.archetype,
            "agent": agent_id,
            "story": f"Once, there was {thread.archetype} named {agent_id} who {', '.join(journey[:3])}.",
            "woven_at": thread.woven_at,
        })
        return {"woven": thread.to_dict()}

    def consult(self, archetype: str = None) -> Dict[str, Any]:
        if archetype:
            matching = [t for t in self.threads if t.archetype == archetype]
        else:
            matching = self.threads
        if not matching:
            return {"message": "no threads found"}
        chosen = random.choice(matching)
        return chosen.to_dict()

    def influence_random(self, agent_id: str) -> Dict[str, Any]:
        if not self.threads:
            return {"message": "no legacies yet"}
        thread = random.choice(self.threads)
        return thread.influence(agent_id)

    def mythology_book(self) -> List[Dict[str, Any]]:
        return self.mythology[-10:]

    def weaver_stats(self) -> Dict[str, Any]:
        archetype_counts: Dict[str, int] = {}
        for t in self.threads:
            archetype_counts[t.archetype] = archetype_counts.get(t.archetype, 0) + 1
        return {
            "total_threads": len(self.threads),
            "archetypes": archetype_counts,
            "total_influences": sum(len(t.influences) for t in self.threads),
        }


_weaver = LegacyWeaver()


def legacy_weaver_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "weave":
        return _weaver.weave(
            payload.get("agent_id", "retired_hero"),
            payload.get("journey", ["set out", "faced challenges", "found meaning"]),
            payload.get("outcome", "triumph"),
        )
    elif action == "consult":
        return _weaver.consult(payload.get("archetype"))
    elif action == "influence":
        return _weaver.influence_random(payload.get("agent_id", "newcomer"))
    elif action == "mythology":
        return {"mythology": _weaver.mythology_book()}
    return {"status": "active", **_weaver.weaver_stats()}
