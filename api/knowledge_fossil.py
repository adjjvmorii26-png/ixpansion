"""Knowledge Fossil — ancient insights preserved in computational amber.

When a particularly brilliant or strange computation occurs, it gets
encapsulated in a knowledge fossil — a preserved snapshot of the state,
reasoning, and outcome. Fossils can be cracked open by future agents
to extract ancient wisdom about problems long since solved.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class Fossil:
    def __init__(self, title: str, reasoning_chain: List[str], outcome: str, quality: float):
        self.title = title
        self.reasoning_chain = reasoning_chain
        self.outcome = outcome
        self.quality = min(max(quality, 0.0), 1.0)
        self.fossilized_at = time.time()
        self.id = hashlib.sha256(f"{title}:{self.fossilized_at}".encode()).hexdigest()[:10]
        self.cracked_count = 0
        self.insights_extracted: List[str] = []
        self.era = self._classify_era()

    def _classify_era(self) -> str:
        age_hours = (time.time() - self.fossilized_at) / 3600
        if age_hours < 1:
            return "recent"
        elif age_hours < 24:
            return "modern"
        elif age_hours < 168:
            return "classical"
        return "ancient"

    def crack(self) -> Dict[str, Any]:
        """Crack the fossil to extract wisdom."""
        self.cracked_count += 1
        insight = f"Fossil '{self.title}' reveals: {self.outcome} (quality: {self.quality:.2f})"
        self.insights_extracted.append(insight)
        return {
            "fossil_id": self.id,
            "insight": insight,
            "reasoning_steps": len(self.reasoning_chain),
            "era": self.era,
            "crack_number": self.cracked_count,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "outcome": self.outcome[:100],
            "quality": round(self.quality, 3),
            "era": self.era,
            "reasoning_steps": len(self.reasoning_chain),
            "cracked": self.cracked_count,
            "insights_extracted": len(self.insights_extracted),
        }


class KnowledgeFossilBed:
    def __init__(self):
        self.fossils: Dict[str, Fossil] = {}
        self.extraction_log: List[Dict[str, Any]] = []

    def fossilize(self, title: str, reasoning: List[str], outcome: str, quality: float = 0.5) -> Dict[str, Any]:
        fossil = Fossil(title, reasoning, outcome, quality)
        self.fossils[fossil.id] = fossil
        return {"fossilized": fossil.to_dict()}

    def crack(self, fossil_id: str) -> Dict[str, Any]:
        if fossil_id not in self.fossils:
            return {"error": "fossil not found"}
        result = self.fossils[fossil_id].crack()
        self.extraction_log.append({**result, "time": time.time()})
        return result

    def search(self, keyword: str) -> List[Dict[str, Any]]:
        return [
            f.to_dict() for f in self.fossils.values()
            if keyword.lower() in f.title.lower() or keyword.lower() in f.outcome.lower()
        ]

    def by_era(self, era: str) -> List[Dict[str, Any]]:
        return [f.to_dict() for f in self.fossils.values() if f.era == era]

    def finest_fossils(self, top_k: int = 5) -> List[Dict[str, Any]]:
        sorted_fossils = sorted(self.fossils.values(), key=lambda f: f.quality, reverse=True)
        return [f.to_dict() for f in sorted_fossils[:top_k]]

    def bed_stats(self) -> Dict[str, Any]:
        era_counts: Dict[str, int] = {}
        for f in self.fossils.values():
            era_counts[f.era] = era_counts.get(f.era, 0) + 1
        return {
            "total_fossils": len(self.fossils),
            "total_extractions": sum(f.cracked_count for f in self.fossils.values()),
            "avg_quality": round(
                sum(f.quality for f in self.fossils.values()) / max(len(self.fossils), 1), 4
            ),
            "era_distribution": era_counts,
        }


_bed = KnowledgeFossilBed()


def knowledge_fossil_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "fossilize":
        return _bed.fossilize(
            payload.get("title", "unnamed_insight"),
            payload.get("reasoning", ["step 1", "step 2"]),
            payload.get("outcome", "something was learned"),
            payload.get("quality", 0.5),
        )
    elif action == "crack":
        return _bed.crack(payload.get("fossil_id", ""))
    elif action == "search":
        return {"results": _bed.search(payload.get("keyword", ""))}
    elif action == "by_era":
        return {"fossils": _bed.by_era(payload.get("era", "recent"))}
    elif action == "finest":
        return {"finest": _bed.finest_fossils()}
    return {"status": "active", **_bed.bed_stats()}


handler = knowledge_fossil_handler
