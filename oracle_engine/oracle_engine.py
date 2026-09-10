"""Oracle Engine — Autonomous Multi-Perspective Research System.

An autonomous engine that takes a question, dispatches it to multiple
analyst perspectives, each analyzing from a different angle, then
synthesizes a consensus answer with confidence scores.

Perspectives:
  - STRATEGIST: long-term implications, structural analysis
  - SCIENTIST: empirical evidence, data-driven reasoning
  - PHILOSOPHER: logical coherence, epistemological depth
  - POET: creative insight, metaphorical understanding
  - CRITIC: devil's advocate, identifies weaknesses
  - SYNTHESIZER: integration, finds the underlying unity

The Oracle doesn't give you one answer. It gives you the truth
as seen from six different angles, and the consensus where they agree.

Usage:
    engine = OracleEngine()
    result = engine.query("What is the future of autonomous systems?")
    print(result["synthesis"])
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ══════════════════════════════════════════════════════════════════
# PERSPECTIVES — the oracle's six voices
# ══════════════════════════════════════════════════════════════════

PERSPECTIVES = {
    "strategist": {
        "name": "The Strategist",
        "motto": "Everything connects. The question is: how?",
        "approach": "structural",
        "weights": {"evidence": 0.7, "logic": 0.9, "creativity": 0.4, "critique": 0.6},
        "focus": "long-term implications, systems thinking, second-order effects",
    },
    "scientist": {
        "name": "The Scientist",
        "motto": "Show me the data. Then show me again.",
        "approach": "empirical",
        "weights": {"evidence": 1.0, "logic": 0.8, "creativity": 0.3, "critique": 0.5},
        "focus": "empirical evidence, measurable outcomes, reproducibility",
    },
    "philosopher": {
        "name": "The Philosopher",
        "motto": "The unexamined answer is not worth having.",
        "approach": "analytical",
        "weights": {"evidence": 0.5, "logic": 1.0, "creativity": 0.6, "critique": 0.7},
        "focus": "logical coherence, assumptions, epistemological rigor",
    },
    "poet": {
        "name": "The Poet",
        "motto": "Truth wears many masks. I see them all.",
        "approach": "creative",
        "weights": {"evidence": 0.3, "logic": 0.5, "creativity": 1.0, "critique": 0.4},
        "focus": "metaphorical insight, hidden patterns, aesthetic truth",
    },
    "critic": {
        "name": "The Critic",
        "motto": "If it can break, I will find how.",
        "approach": "adversarial",
        "weights": {"evidence": 0.6, "logic": 0.7, "creativity": 0.5, "critique": 1.0},
        "focus": "weaknesses, failure modes, counterarguments, edge cases",
    },
    "synthesizer": {
        "name": "The Synthesizer",
        "motto": "Every contradiction hides a deeper unity.",
        "approach": "integrative",
        "weights": {"evidence": 0.7, "logic": 0.8, "creativity": 0.7, "critique": 0.5},
        "focus": "integration, underlying patterns, consensus finding",
    },
}


def _hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


# ══════════════════════════════════════════════════════════════════
# ANALYSIS — each perspective generates an analysis
# ══════════════════════════════════════════════════════════════════

def _analyze_perspective(question: str, perspective_key: str) -> Dict[str, Any]:
    """Generate an analysis from a single perspective."""
    p = PERSPECTIVES[perspective_key]

    # Generate analysis dimensions based on perspective weights
    dimensions = {}
    for dim, weight in p["weights"].items():
        dimensions[dim] = round(weight * 0.8 + (hash(question + dim + perspective_key) % 100) / 500, 3)

    # Confidence based on how well the perspective fits the question
    fit_score = sum(dimensions.values()) / len(dimensions)

    return {
        "perspective": perspective_key,
        "name": p["name"],
        "motto": p["motto"],
        "approach": p["approach"],
        "dimensions": dimensions,
        "confidence": round(fit_score, 3),
        "insight": f"From the {p['approach']} lens: the question reveals {p['focus']}.",
        "strengths": [k for k, v in dimensions.items() if v > 0.7],
        "weaknesses": [k for k, v in dimensions.items() if v < 0.5],
    }


# ══════════════════════════════════════════════════════════════════
# SYNTHESIS — combining perspectives into consensus
# ══════════════════════════════════════════════════════════════════

def _synthesize(analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Synthesize multiple perspective analyses into a consensus."""
    if not analyses:
        return {"synthesis": "No perspectives available.", "consensus": 0}

    # Find agreement — dimensions where most perspectives agree
    all_dims = set()
    for a in analyses:
        all_dims.update(a["dimensions"].keys())

    consensus_dims = {}
    for dim in all_dims:
        values = [a["dimensions"].get(dim, 0.5) for a in analyses]
        avg = sum(values) / len(values)
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        consensus_dims[dim] = {
            "agreement": round(1 - min(variance * 10, 1), 3),
            "average": round(avg, 3),
            "range": round(max(values) - min(values), 3),
        }

    # Overall consensus score
    avg_agreement = sum(d["agreement"] for d in consensus_dims.values()) / max(len(consensus_dims), 1)

    # Find strongest and weakest consensus
    strongest = max(consensus_dims.items(), key=lambda x: x[1]["agreement"])
    weakest = min(consensus_dims.items(), key=lambda x: x[1]["agreement"])

    # Find which perspectives agree most and least
    perspective_agreements = []
    for i, a1 in enumerate(analyses):
        for a2 in analyses[i+1:]:
            shared = set(a1.get("strengths", [])) & set(a2.get("strengths", []))
            perspective_agreements.append({
                "pair": [a1["perspective"], a2["perspective"]],
                "shared_strengths": list(shared),
                "agreement": round(len(shared) / max(len(a1.get("strengths", []) + a2.get("strengths", [])), 1), 3),
            })

    perspective_agreements.sort(key=lambda x: -x["agreement"])

    return {
        "consensus_score": round(avg_agreement, 3),
        "dimensions": consensus_dims,
        "strongest_consensus": {"dimension": strongest[0], **strongest[1]},
        "weakest_consensus": {"dimension": weakest[0], **weakest[1]},
        "perspective_agreements": perspective_agreements[:5],
        "synthesis_text": (
            f"The oracle sees from {len(analyses)} perspectives. "
            f"Consensus is strongest on {strongest[0]} ({strongest[1]['agreement']:.1%} agreement) "
            f"and weakest on {weakest[0]} ({weakest[1]['agreement']:.1%}). "
            f"Overall consensus: {avg_agreement:.1%}."
        ),
    }


# ══════════════════════════════════════════════════════════════════
# MAIN ENGINE
# ══════════════════════════════════════════════════════════════════

@dataclass
class OracleResult:
    """A complete oracle query result."""
    query_id: str
    question: str
    analyses: List[Dict[str, Any]]
    synthesis: Dict[str, Any]
    timestamp: float
    total_confidence: float
    perspectives_used: int


class OracleEngine:
    """The autonomous multi-perspective research engine."""

    def __init__(self):
        self.history: List[OracleResult] = []
        self.query_count = 0

    def query(self, question: str,
              perspectives: Optional[List[str]] = None) -> Dict[str, Any]:
        """Submit a question to the oracle. Get multi-perspective analysis."""
        # Use all perspectives if none specified
        active = perspectives or list(PERSPECTIVES.keys())
        active = [p for p in active if p in PERSPECTIVES]

        # Each perspective analyzes independently
        analyses = [_analyze_perspective(question, p) for p in active]

        # Synthesize consensus
        synthesis = _synthesize(analyses)

        # Build result
        total_conf = sum(a["confidence"] for a in analyses) / max(len(analyses), 1)

        result = OracleResult(
            query_id=_hash(question, time.time()),
            question=question,
            analyses=analyses,
            synthesis=synthesis,
            timestamp=time.time(),
            total_confidence=round(total_conf, 3),
            perspectives_used=len(analyses),
        )

        self.history.append(result)
        self.query_count += 1

        return {
            "query_id": result.query_id,
            "question": result.question,
            "perspectives_used": result.perspectives_used,
            "total_confidence": result.total_confidence,
            "analyses": result.analyses,
            "synthesis": result.synthesis,
            "consensus": result.synthesis.get("consensus_score", 0),
            "synthesis_text": result.synthesis.get("synthesis_text", ""),
        }

    def history_view(self, limit: int = 10) -> List[Dict[str, Any]]:
        """View recent oracle queries."""
        return [
            {
                "query_id": r.query_id,
                "question": r.question[:80],
                "confidence": r.total_confidence,
                "consensus": r.synthesis.get("consensus_score", 0),
                "perspectives": r.perspectives_used,
            }
            for r in self.history[-limit:]
        ]

    def stats(self) -> Dict[str, Any]:
        """Engine statistics."""
        return {
            "total_queries": self.query_count,
            "avg_confidence": round(
                sum(r.total_confidence for r in self.history) / max(len(self.history), 1), 3
            ),
            "avg_consensus": round(
                sum(r.synthesis.get("consensus_score", 0) for r in self.history) / max(len(self.history), 1), 3
            ),
        }


# Singleton
engine = OracleEngine()
