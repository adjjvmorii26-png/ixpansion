"""Innovation Pipeline — transforms raw ideas into production-ready features.

Ideas enter the pipeline as rough concepts. They pass through stages:
ideation, validation, prototyping, testing, and deployment. Each stage
filters and refines. Only the most viable innovations emerge at the end.
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

STAGES = ["ideation", "validation", "prototyping", "testing", "deployment"]


class Innovation:
    def __init__(self, name: str, description: str, proposer: str):
        self.name = name
        self.description = description
        self.proposer = proposer
        self.stage_idx = 0
        self.stage_history: List[Dict[str, Any]] = []
        self.viability_score = random.uniform(0.3, 0.9)
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{name}:{self.created_at}".encode()).hexdigest()[:8]
        self.eliminated = False
        self.notes: List[str] = []

    @property
    def current_stage(self) -> str:
        if self.eliminated:
            return "eliminated"
        return STAGES[min(self.stage_idx, len(STAGES) - 1)]

    def advance(self) -> Dict[str, Any]:
        if self.eliminated:
            return {"status": "eliminated"}
        gate = random.uniform(0.0, 1.0)
        if gate > self.viability_score * 0.8:
            self.eliminated = True
            self.stage_history.append({
                "stage": self.current_stage, "result": "eliminated",
                "time": time.time(),
            })
            return {"status": "eliminated at " + STAGES[self.stage_idx]}
        self.stage_idx += 1
        self.viability_score += random.uniform(-0.05, 0.1)
        self.viability_score = min(max(self.viability_score, 0.0), 1.0)
        result = {
            "name": self.name,
            "from_stage": STAGES[min(self.stage_idx - 1, len(STAGES) - 1)],
            "to_stage": self.current_stage,
            "viability": round(self.viability_score, 3),
        }
        self.stage_history.append({**result, "time": time.time()})
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description[:80],
            "proposer": self.proposer,
            "stage": self.current_stage,
            "viability": round(self.viability_score, 3),
            "eliminated": self.eliminated,
            "stage_number": self.stage_idx,
        }


class InnovationPipeline:
    def __init__(self):
        self.innovations: Dict[str, Innovation] = []
        self.deployed: List[Dict[str, Any]] = []

    def submit(self, name: str, description: str, proposer: str) -> Dict[str, Any]:
        innovation = Innovation(name, description, proposer)
        self.innovations.append(innovation)
        return {"submitted": innovation.to_dict()}

    def advance_all(self) -> List[Dict[str, Any]]:
        results = []
        for innovation in self.innovations:
            if not innovation.eliminated:
                result = innovation.advance()
                results.append(result)
                if innovation.current_stage == "deployment" and not innovation.eliminated:
                    self.deployed.append(innovation.to_dict())
        return results

    def pipeline_view(self) -> List[Dict[str, Any]]:
        view: Dict[str, List[Dict[str, Any]]] = {stage: [] for stage in STAGES}
        view["eliminated"] = []
        for innovation in self.innovations:
            if innovation.eliminated:
                view["eliminated"].append(innovation.to_dict())
            else:
                view[innovation.current_stage].append(innovation.to_dict())
        return view

    def pipeline_stats(self) -> Dict[str, Any]:
        stage_counts: Dict[str, int] = {}
        for innovation in self.innovations:
            stage = innovation.current_stage
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        return {
            "total_submitted": len(self.innovations),
            "deployed": len(self.deployed),
            "eliminated": stage_counts.get("eliminated", 0),
            "in_pipeline": len(self.innovations) - stage_counts.get("eliminated", 0),
            "stage_distribution": stage_counts,
        }


_pipeline = InnovationPipeline()


def innovation_pipeline_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "submit":
        return _pipeline.submit(
            payload.get("name", f"idea_{random.randint(100,999)}"),
            payload.get("description", "a novel idea"),
            payload.get("proposer", "innovator"),
        )
    elif action == "advance":
        return {"advancements": _pipeline.advance_all()}
    elif action == "view":
        return {"pipeline": _pipeline.pipeline_view()}
    return {"status": "active", **_pipeline.pipeline_stats()}


handler = innovation_pipeline_handler
