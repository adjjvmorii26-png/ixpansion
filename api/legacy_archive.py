"""Legacy Archive — preserves retired agents as cultural artifacts.

When agents are retired, they don't just vanish. Their history, decisions,
and personality are preserved as cultural artifacts. Future agents can
consult the archive for wisdom, learn from past mistakes, and carry
forward the legacy of their predecessors.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class LegacyArtifact:
    def __init__(self, agent_id: str, history: List[Dict[str, Any]], personality: Dict[str, Any]):
        self.agent_id = agent_id
        self.history = history
        self.personality = personality
        self.archived_at = time.time()
        self.id = hashlib.sha256(f"{agent_id}:{self.archived_at}".encode()).hexdigest()[:8]
        self.wisdom_score = random.uniform(0.3, 1.0)
        self.consultations = 0

    def consult(self, question: str) -> Dict[str, Any]:
        self.consultations += 1
        relevant_memories = [
            h for h in self.history
            if any(word in str(h).lower() for word in question.lower().split())
        ]
        wisdom = random.choice(relevant_memories) if relevant_memories else {
            "lesson": f"From the era of {self.agent_id}: patience reveals what haste obscures."
        }
        return {
            "archived_agent": self.agent_id,
            "question": question,
            "wisdom": wisdom,
            "relevance": round(random.uniform(0.3, 0.9), 3),
            "total_consultations": self.consultations,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "archived_at": self.archived_at,
            "history_size": len(self.history),
            "personality_traits": list(self.personality.keys()),
            "wisdom_score": round(self.wisdom_score, 3),
            "consultations": self.consultations,
        }


class LegacyArchive:
    def __init__(self):
        self.artifacts: Dict[str, LegacyArtifact] = {}
        self.retirement_log: List[Dict[str, Any]] = []

    def archive(self, agent_id: str, history: List[Dict[str, Any]], personality: Dict[str, Any]) -> Dict[str, Any]:
        artifact = LegacyArtifact(agent_id, history, personality)
        self.artifacts[artifact.id] = artifact
        self.retirement_log.append({
            "agent": agent_id, "archived_at": artifact.archived_at,
            "history_entries": len(history),
        })
        return {"archived": artifact.to_dict()}

    def consult(self, artifact_id: str, question: str) -> Dict[str, Any]:
        if artifact_id not in self.artifacts:
            return {"error": "artifact not found"}
        return self.artifacts[artifact_id].consult(question)

    def search(self, keyword: str) -> List[Dict[str, Any]]:
        results = []
        for artifact in self.artifacts.values():
            if keyword.lower() in artifact.agent_id.lower():
                results.append(artifact.to_dict())
        return results

    def oldest_wisdom(self) -> Optional[Dict[str, Any]]:
        if not self.artifacts:
            return None
        oldest = min(self.artifacts.values(), key=lambda a: a.archived_at)
        return oldest.to_dict()

    def most_consulted(self, top_k: int = 3) -> List[Dict[str, Any]]:
        sorted_artifacts = sorted(self.artifacts.values(), key=lambda a: a.consultations, reverse=True)
        return [a.to_dict() for a in sorted_artifacts[:top_k]]

    def archive_stats(self) -> Dict[str, Any]:
        return {
            "total_artifacts": len(self.artifacts),
            "total_consultations": sum(a.consultations for a in self.artifacts.values()),
            "avg_wisdom_score": round(
                sum(a.wisdom_score for a in self.artifacts.values()) / max(len(self.artifacts), 1), 4
            ),
        }


_archive = LegacyArchive()


def legacy_archive_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "archive":
        return _archive.archive(
            payload.get("agent_id", f"retired_{random.randint(100,999)}"),
            payload.get("history", []),
            payload.get("personality", {}),
        )
    elif action == "consult":
        return _archive.consult(payload.get("artifact_id", ""), payload.get("question", ""))
    elif action == "search":
        return {"results": _archive.search(payload.get("keyword", ""))}
    elif action == "oldest":
        return _archive.oldest_wisdom() or {"message": "archive is empty"}
    elif action == "most_consulted":
        return {"top": _archive.most_consulted()}
    return {"status": "active", **_archive.archive_stats()}


handler = legacy_archive_handler
