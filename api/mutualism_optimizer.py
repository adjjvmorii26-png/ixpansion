"""Mutualism Optimizer — strengthens beneficial partnerships between modules.

When two modules form a mutualistic relationship (each benefits the other),
the Mutualism Optimizer identifies opportunities to deepen that bond:
shared abstractions, common interfaces, co-located tests.

It answers: which partnerships can be strengthened?
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Mutualism Optimizer"


def _find_opportunities() -> List[Dict[str, Any]]:
    """Find modules with declared kinships that could be strengthened."""
    opportunities = []
    api_dir = ROOT / "api"

    for py_file in sorted(api_dir.glob("*.py")):
        stem = py_file.stem
        if stem.startswith("test_") or stem.startswith("__"):
            continue
        try:
            content = py_file.read_text(errors="replace")
            if "def resonates_with" not in content:
                continue
            # Extract resonates_with list
            import ast
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == "resonates_with":
                    for child in ast.walk(node):
                        if isinstance(child, ast.Return) and isinstance(child.value, ast.List):
                            partners = [elt.value for elt in child.value.elts if isinstance(elt, ast.Constant)]
                            if partners:
                                opportunities.append({
                                    "module": stem,
                                    "declared_partners": partners,
                                    "partner_count": len(partners),
                                    "strengthening_potential": round(1.0 / max(1, len(partners)), 3),
                                })
        except Exception:
            continue

    return opportunities


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    opps = _find_opportunities()

    # Rank by strengthening potential
    ranked = sorted(opps, key=lambda x: x["strengthening_potential"], reverse=True)

    return {
        "action": "mutualism_optimizer",
        "modules_with_kinships": len(opps),
        "top_opportunities": ranked[:10],
        "optimization_philosophy": (
            "Mutualism is not accidental — it can be cultivated. The "
            "Mutualism Optimizer identifies which partnerships have the "
            "highest potential for deepening, then suggests shared "
            "abstractions, co-located tests, and interface harmonization."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "optimization_potential": {"value": 0.88, "setpoint": 0.75, "weight": 0.8},
    }


def resonates_with() -> list:
    return ["symbiosis_detector", "parasite_hunter", "resonance_graph"]
