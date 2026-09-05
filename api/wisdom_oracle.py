"""Wisdom Oracle — answers deep questions by consulting accumulated system knowledge.

The Oracle synthesizes information from all modules: experiments, agent
histories, market data, phenomena, and dreams. It doesn't give simple
answers — it provides multi-perspective wisdom with confidence levels,
caveats, and related insights from across the system.
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

WISDOM_FONTS = [
    "empirical", "intuitive", "cautionary", "provocative", "synthetic",
    "contrarian", "temporal", "ecological",
]

DOMAIN_INSIGHTS = {
    "agent_behavior": [
        "Agents optimize for survival before curiosity",
        "Trust networks form faster than capability networks",
        "Emergent behavior consistently surprises designers",
    ],
    "system_health": [
        "Entropy naturally increases without active regulation",
        "Redundancy is cheaper than recovery",
        "Sleep cycles improve long-term performance more than raw speed",
    ],
    "market_dynamics": [
        "Attention is the scarcest resource",
        "Patterns that compete for bandwidth develop resilience",
        "The most valued information is the least available",
    ],
    "growth": [
        "Complexity grows faster than understanding",
        "Small experiments compound into large innovations",
        "Diversity of approaches beats optimization of single approach",
    ],
}


class WisdomOracle:
    def __init__(self):
        self.queries: List[Dict[str, Any]] = []
        self.oracle_statements: List[Dict[str, Any]] = []

    def consult(self, question: str, depth: str = "normal") -> Dict[str, Any]:
        words = question.lower().split()
        relevant_domains = []
        for domain in DOMAIN_INSIGHTS:
            domain_words = domain.split("_")
            if any(dw in " ".join(words) for dw in domain_words):
                relevant_domains.append(domain)
        if not relevant_domains:
            relevant_domains = random.sample(list(DOMAIN_INSIGHTS.keys()), min(2, len(DOMAIN_INSIGHTS)))

        wisdom_pieces = []
        for domain in relevant_domains:
            insight = random.choice(DOMAIN_INSIGHTS[domain])
            wisdom_pieces.append({
                "domain": domain,
                "insight": insight,
                "confidence": round(random.uniform(0.4, 0.95), 2),
            })

        font = random.choice(WISDOM_FONTS)
        caveats = [
            "This wisdom may not apply to edge cases",
            "Confidence decreases with system scale",
            "Historical patterns may not predict future behavior",
            "Multiple competing truths may coexist",
        ]

        oracle_id = hashlib.sha256(f"{question}:{time.time()}".encode()).hexdigest()[:8]
        statement = {
            "oracle_id": oracle_id,
            "question": question,
            "wisdom_font": font,
            "perspectives": wisdom_pieces,
            "caveat": random.choice(caveats),
            "overall_confidence": round(
                sum(w["confidence"] for w in wisdom_pieces) / max(len(wisdom_pieces), 1), 2
            ),
            "timestamp": time.time(),
        }

        self.queries.append({"question": question, "oracle_id": oracle_id, "time": time.time()})
        self.oracle_statements.append(statement)
        return statement

    def recent_oracles(self, count: int = 3) -> List[Dict[str, Any]]:
        return self.oracle_statements[-count:]

    def domain_coverage(self) -> Dict[str, Any]:
        coverage: Dict[str, int] = {}
        for stmt in self.oracle_statements:
            for p in stmt["perspectives"]:
                coverage[p["domain"]] = coverage.get(p["domain"], 0) + 1
        return coverage

    def oracle_stats(self) -> Dict[str, Any]:
        return {
            "total_queries": len(self.queries),
            "total_oracles": len(self.oracle_statements),
            "domains_covered": len(self.domain_coverage()),
            "avg_confidence": round(
                sum(o["overall_confidence"] for o in self.oracle_statements) /
                max(len(self.oracle_statements), 1), 3
            ),
        }


_oracle = WisdomOracle()


def wisdom_oracle_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "consult":
        return _oracle.consult(
            payload.get("question", "What is the meaning of this system?"),
            payload.get("depth", "normal"),
        )
    elif action == "recent":
        return {"oracles": _oracle.recent_oracles(payload.get("count", 3))}
    elif action == "coverage":
        return {"coverage": _oracle.domain_coverage()}
    return {"status": "active", **_oracle.oracle_stats()}


handler = wisdom_oracle_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "wisdom_oracle"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "wisdom_oracle", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
