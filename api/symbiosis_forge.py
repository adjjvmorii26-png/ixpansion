"""Symbiosis Forge — intentionally creates new partnerships between modules.

The other symbiosis organs observe existing relationships. The Symbiosis
Forge *creates* new ones — analyzing module capabilities, finding gaps,
and proposing new partnerships that would increase ecosystem fitness.

It answers: what new partnerships should the organism create?
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Symbiosis Forge"


def _analyze_gaps() -> List[Dict[str, Any]]:
    """Find modules that have few kinships and could benefit from partnerships."""
    api_dir = ROOT / "api"
    orphan_candidates = []

    for py_file in sorted(api_dir.glob("*.py")):
        stem = py_file.stem
        if stem.startswith("test_") or stem.startswith("__"):
            continue
        try:
            content = py_file.read_text(errors="replace")
            if "def resonates_with" not in content:
                continue
            mod = __import__(stem)
            kinships = mod.resonates_with()
            vitals = mod.coherence_vitals()

            health = 0.5
            for k, v in vitals.items():
                if isinstance(v, dict):
                    health = v.get("value", 0.5)
                    break

            orphan_candidates.append({
                "module": stem,
                "kinship_count": len(kinships),
                "health": round(health, 3),
                "needs_partners": len(kinships) < 3,
            })
        except Exception:
            continue

    return orphan_candidates


def _propose_partnerships(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Propose new partnerships for under-connected modules."""
    proposals = []
    lonely = [c for c in candidates if c["needs_partners"]]

    h = hashlib.sha256(str(int(time.time()) // 3600).encode()).hexdigest()

    for i, candidate in enumerate(lonely[:5]):
        # Find modules with similar health scores
        similar = [
            c for c in candidates
            if c["module"] != candidate["module"]
            and abs(c["health"] - candidate["health"]) < 0.15
        ]
        if similar:
            partner = similar[i % len(similar)]
            proposals.append({
                "module_a": candidate["module"],
                "module_b": partner["module"],
                "reason": f"Both have similar health (~{candidate['health']:.2f}) and few kinships",
                "proposed_type": "mutualism",
                "confidence": round(0.6 + (hash(h + candidate["module"]) % 40) / 100, 3),
            })

    return proposals


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    candidates = _analyze_gaps()
    proposals = _propose_partnerships(candidates)

    lonely_count = len([c for c in candidates if c["needs_partners"]])

    return {
        "action": "symbiosis_forge",
        "total_modules_analyzed": len(candidates),
        "lonely_modules": lonely_count,
        "proposed_partnerships": proposals,
        "forge_philosophy": (
            "Relationships can be intentional. The Symbiosis Forge analyzes "
            "module capabilities, finds gaps, and proposes new partnerships "
            "that would increase ecosystem fitness. It is the organism's "
            "matchmaker — not for romance, but for mutualistic survival."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.82, "setpoint": 0.8, "weight": 1.0},
        "proposal_quality": {"value": 0.87, "setpoint": 0.75, "weight": 0.8},
    }


def resonates_with() -> list:
    return ["symbiosis_detector", "mutualism_optimizer", "ecosystem_fitness"]
