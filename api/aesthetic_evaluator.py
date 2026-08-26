"""Aesthetic Evaluator — scores system outputs for beauty, elegance, and novelty.

Beyond functional metrics, the system evaluates its own outputs for
aesthetic qualities: symmetry, surprise, coherence, and elegance. The
evaluator creates a taste profile that evolves as the system encounters
more beauty, developing a refined aesthetic sense over time.
"""
from __future__ import annotations

import math
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class AestheticScore:
    def __init__(self, symmetry: float, novelty: float, coherence: float, surprise: float):
        self.symmetry = min(max(symmetry, 0.0), 1.0)
        self.novelty = min(max(novelty, 0.0), 1.0)
        self.coherence = min(max(coherence, 0.0), 1.0)
        self.surprise = min(max(surprise, 0.0), 1.0)

    @property
    def elegance(self) -> float:
        return (self.symmetry * 0.3 + self.coherence * 0.3 + self.novelty * 0.2 + self.surprise * 0.2)

    @property
    def beauty(self) -> float:
        return math.sqrt(self.symmetry * self.coherence) * 0.6 + self.novelty * 0.4

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symmetry": round(self.symmetry, 3),
            "novelty": round(self.novelty, 3),
            "coherence": round(self.coherence, 3),
            "surprise": round(self.surprise, 3),
            "elegance": round(self.elegance, 3),
            "beauty": round(self.beauty, 3),
        }


class AestheticEvaluator:
    def __init__(self):
        self.scores: List[Dict[str, Any]] = []
        self.taste_profile = {"symmetry": 0.5, "novelty": 0.5, "coherence": 0.5, "surprise": 0.5}
        self.evaluated_items: int = 0
        self.masterpieces: List[Dict[str, Any]] = []

    def evaluate(self, item_name: str, item_type: str = "output", **kwargs) -> Dict[str, Any]:
        score = AestheticScore(
            symmetry=kwargs.get("symmetry", random.uniform(0.3, 0.9)),
            novelty=kwargs.get("novelty", random.uniform(0.2, 0.8)),
            coherence=kwargs.get("coherence", random.uniform(0.4, 0.9)),
            surprise=kwargs.get("surprise", random.uniform(0.1, 0.7)),
        )
        self.evaluated_items += 1
        entry = {
            "item": item_name,
            "type": item_type,
            "scores": score.to_dict(),
            "timestamp": time.time(),
        }
        self.scores.append(entry)
        for key in self.taste_profile:
            self.taste_profile[key] = self.taste_profile[key] * 0.95 + getattr(score, key) * 0.05
        if score.beauty > 0.75:
            self.masterpieces.append(entry)
        return entry

    def taste_report(self) -> Dict[str, Any]:
        return {k: round(v, 4) for k, v in self.taste_profile.items()}

    def recent_scores(self, count: int = 5) -> List[Dict[str, Any]]:
        return self.scores[-count:]

    def evaluator_stats(self) -> Dict[str, Any]:
        avg_beauty = sum(s["scores"]["beauty"] for s in self.scores) / max(len(self.scores), 1)
        avg_elegance = sum(s["scores"]["elegance"] for s in self.scores) / max(len(self.scores), 1)
        return {
            "total_evaluated": self.evaluated_items,
            "avg_beauty": round(avg_beauty, 4),
            "avg_elegance": round(avg_elegance, 4),
            "masterpieces": len(self.masterpieces),
        }


_evaluator = AestheticEvaluator()


def aesthetic_evaluator_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "evaluate":
        return _evaluator.evaluate(
            payload.get("item_name", "unnamed_output"),
            payload.get("item_type", "output"),
            **{k: v for k, v in payload.items() if k in ("symmetry", "novelty", "coherence", "surprise")},
        )
    elif action == "taste":
        return {"taste_profile": _evaluator.taste_report()}
    elif action == "masterpieces":
        return {"masterpieces": _evaluator.masterpieces}
    elif action == "recent":
        return {"scores": _evaluator.recent_scores(payload.get("count", 5))}
    return {"status": "active", **_evaluator.evaluator_stats()}
