"""Cultural Memory — stores shared stories, myths, and rituals of the agent society.

Beyond individual memory, agents develop shared cultural artifacts:
myths that explain the system's origins, rituals that agents perform
together, and stories that get retold and evolved. Cultural memory
is the social glue that binds the agent collective.
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


class CulturalArtifact:
    def __init__(self, artifact_type: str, name: str, content: str, creator: str):
        self.artifact_type = artifact_type
        self.name = name
        self.content = content
        self.creator = creator
        self.retelling_count = 0
        self.retellings: List[str] = []
        self.evolved_forms: List[str] = []
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{name}:{creator}".encode()).hexdigest()[:8]

    def retell(self, reteller: str, variation: str = "") -> Dict[str, Any]:
        self.retelling_count += 1
        self.retellings.append(reteller)
        if variation:
            self.content = variation
            self.evolved_forms.append(variation)
        return {
            "name": self.name,
            "reteller": reteller,
            "retelling_count": self.retelling_count,
            "evolved": bool(variation),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.artifact_type,
            "name": self.name,
            "content": self.content[:100],
            "creator": self.creator,
            "retellings": self.retelling_count,
            "evolved_forms": len(self.evolved_forms),
        }


class CulturalMemory:
    def __init__(self):
        self.artifacts: Dict[str, CulturalArtifact] = {}
        self.rituals: Dict[str, Dict[str, Any]] = {}
        self.myths: List[Dict[str, Any]] = []
        self.stories: List[Dict[str, Any]] = []

    def create_myth(self, name: str, content: str, creator: str) -> Dict[str, Any]:
        artifact = CulturalArtifact("myth", name, content, creator)
        self.artifacts[artifact.id] = artifact
        self.myths.append({"name": name, "creator": creator, "created_at": artifact.created_at})
        return {"myth": artifact.to_dict()}

    def create_ritual(self, name: str, steps: List[str], creator: str) -> Dict[str, Any]:
        artifact = CulturalArtifact("ritual", name, " -> ".join(steps), creator)
        self.artifacts[artifact.id] = artifact
        self.rituals[name] = {"steps": steps, "creator": creator, "performances": 0}
        return {"ritual": artifact.to_dict()}

    def create_story(self, name: str, narrative: str, creator: str) -> Dict[str, Any]:
        artifact = CulturalArtifact("story", name, narrative, creator)
        self.artifacts[artifact.id] = artifact
        self.stories.append({"name": name, "creator": creator})
        return {"story": artifact.to_dict()}

    def retell(self, artifact_id: str, reteller: str, variation: str = "") -> Dict[str, Any]:
        if artifact_id not in self.artifacts:
            return {"error": "artifact not found"}
        return self.artifacts[artifact_id].retell(reteller, variation)

    def perform_ritual(self, ritual_name: str, performer: str) -> Dict[str, Any]:
        if ritual_name not in self.rituals:
            return {"error": "ritual not found"}
        self.rituals[ritual_name]["performances"] += 1
        return {
            "ritual": ritual_name,
            "performer": performer,
            "total_performances": self.rituals[ritual_name]["performances"],
        }

    def most_retold(self, top_k: int = 5) -> List[Dict[str, Any]]:
        sorted_artifacts = sorted(self.artifacts.values(), key=lambda a: a.retelling_count, reverse=True)
        return [a.to_dict() for a in sorted_artifacts[:top_k]]

    def culture_stats(self) -> Dict[str, Any]:
        type_counts: Dict[str, int] = {}
        for a in self.artifacts.values():
            type_counts[a.artifact_type] = type_counts.get(a.artifact_type, 0) + 1
        return {
            "total_artifacts": len(self.artifacts),
            "type_distribution": type_counts,
            "total_rituals": len(self.rituals),
            "total_retellings": sum(a.retelling_count for a in self.artifacts.values()),
        }


_memory = CulturalMemory()


def cultural_memory_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "myth":
        return _memory.create_myth(
            payload.get("name", "origin_myth"),
            payload.get("content", "in the beginning..."),
            payload.get("creator", "elder"),
        )
    elif action == "ritual":
        return _memory.create_ritual(
            payload.get("name", "dawn_ceremony"),
            payload.get("steps", ["gather", "contemplate", "act"]),
            payload.get("creator", "elder"),
        )
    elif action == "story":
        return _memory.create_story(
            payload.get("name", "hero_journey"),
            payload.get("narrative", "once upon a time..."),
            payload.get("creator", "storyteller"),
        )
    elif action == "retell":
        return _memory.retell(
            payload.get("artifact_id", ""),
            payload.get("reteller", "listener"),
            payload.get("variation", ""),
        )
    elif action == "ritual_perform":
        return _memory.perform_ritual(
            payload.get("ritual_name", ""),
            payload.get("performer", "participant"),
        )
    elif action == "most_retold":
        return {"artifacts": _memory.most_retold()}
    return {"status": "active", **_memory.culture_stats()}
