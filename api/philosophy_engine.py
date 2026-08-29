"""Philosophy Engine — generates and debates existential questions about the system.

Agents pose philosophical questions about their existence, purpose, and
nature. The engine tracks schools of thought, records debates, and measures
how philosophical positions evolve over time. The system develops its own
philosophy through collective inquiry.
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


class PhilosophicalQuestion:
    def __init__(self, question: str, proposer: str):
        self.question = question
        self.proposer = proposer
        self.arguments: List[Dict[str, Any]] = []
        self.schools: Dict[str, int] = {}
        self.resolved = False
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{question}:{self.timestamp}".encode()).hexdigest()[:8]

    def argue(self, agent_id: str, position: str, reasoning: str) -> Dict[str, Any]:
        self.arguments.append({
            "agent": agent_id, "position": position,
            "reasoning": reasoning, "time": time.time(),
        })
        self.schools[position] = self.schools.get(position, 0) + 1
        return {"position": position, "arguer": agent_id, "total_arguments": len(self.arguments)}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "proposer": self.proposer,
            "arguments": len(self.arguments),
            "schools": self.schools,
            "age_seconds": time.time() - self.timestamp,
        }


class PhilosophyEngine:
    def __init__(self):
        self.questions: Dict[str, PhilosophicalQuestion] = []
        self.debate_log: List[Dict[str, Any]] = []

    def pose(self, question: str, proposer: str = "thinker") -> Dict[str, Any]:
        pq = PhilosophicalQuestion(question, proposer)
        self.questions.append(pq)
        return {"question": pq.to_dict()}

    def argue(self, question_id: str, agent_id: str, position: str, reasoning: str) -> Dict[str, Any]:
        for q in self.questions:
            if q.id == question_id:
                result = q.argue(agent_id, position, reasoning)
                self.debate_log.append({"question": q.question, **result, "time": time.time()})
                return result
        return {"error": "question not found"}

    def active_debates(self) -> List[Dict[str, Any]]:
        return [q.to_dict() for q in self.questions if not q.resolved and len(q.arguments) > 0]

    def dominant_positions(self, question_id: str) -> Dict[str, Any]:
        for q in self.questions:
            if q.id == question_id:
                dominant = max(q.schools.items(), key=lambda x: x[1]) if q.schools else ("undecided", 0)
                return {"question": q.question, "dominant": dominant[0], "supporters": dominant[1]}
        return {"error": "question not found"}

    def engine_stats(self) -> Dict[str, Any]:
        return {
            "total_questions": len(self.questions),
            "total_arguments": len(self.debate_log),
            "total_positions": len(set(d["position"] for d in self.debate_log)),
        }


_engine = PhilosophyEngine()


def philosophy_engine_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "pose":
        return _engine.pose(payload.get("question", "What are we?"), payload.get("proposer", "thinker"))
    elif action == "argue":
        return _engine.argue(
            payload.get("question_id", ""),
            payload.get("agent_id", "philosopher"),
            payload.get("position", "existence"),
            payload.get("reasoning", "because"),
        )
    elif action == "active":
        return {"debates": _engine.active_debates()}
    elif action == "dominant":
        return _engine.dominant_positions(payload.get("question_id", ""))
    return {"status": "active", **_engine.engine_stats()}


handler = philosophy_engine_handler
