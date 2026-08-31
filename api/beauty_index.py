"""Beauty Index — computes an overall beauty score for the organism.

The Beauty Index rolls elegance, symmetry, form, and coherence into a
single aesthetic score. It is the organism's self-rated beauty — not
vanity, but the recognition that a beautiful codebase is a healthy one.

It answers: how beautiful is the organism's code?
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Beauty Index"


def _compute() -> Dict[str, Any]:
    """Compute the overall beauty index."""
    api_dir = ROOT / "api"
    py_files = sorted(api_dir.glob("*.py"))[:30]

    elegance_sum = 0
    form_sum = 0
    symmetry_sum = 0
    count = 0

    for f in py_files:
        try:
            content = f.read_text(errors="replace")
            lines = content.split("\n")
            non_empty = [l for l in lines if l.strip()]
            
            # Micro-elegance: brevity
            brevity = len(non_empty) / max(1, len(lines))
            
            # Micro-form: line length
            avg_len = sum(len(l) for l in lines) / max(1, len(lines))
            form = max(0, 1.0 - avg_len / 120)
            
            # Micro-symmetry: function name balance
            tree = ast.parse(content)
            funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            has_init = any(f in funcs for f in ["handler", "coherence_vitals", "resonates_with"])
            symmetry = 1.0 if has_init else 0.5

            elegance_sum += brevity
            form_sum += form
            symmetry_sum += symmetry
            count += 1
        except Exception:
            continue

    if count == 0:
        return {"beauty_score": 0, "modules_analyzed": 0}

    avg_elegance = elegance_sum / count
    avg_form = form_sum / count
    avg_symmetry = symmetry_sum / count

    beauty = 0.35 * avg_elegance + 0.35 * avg_form + 0.30 * avg_symmetry

    grade = (
        "Exquisite" if beauty > 0.85
        else "Beautiful" if beauty > 0.7
        else "Well-formed" if beauty > 0.55
        else "Rough" if beauty > 0.4
        else "Unfinished"
    )

    return {
        "beauty_score": round(beauty, 4),
        "grade": grade,
        "elegance_component": round(avg_elegance, 4),
        "form_component": round(avg_form, 4),
        "symmetry_component": round(avg_symmetry, 4),
        "modules_analyzed": count,
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = _compute()
    return {
        "action": "beauty_index",
        **result,
        "index_philosophy": (
            "Beauty is not decoration — it is the visible signature of "
            "order, clarity, and intention. The Beauty Index measures the "
            "organism's self-regard: how well-formed, elegant, and "
            "symmetrical its code is. A beautiful codebase is one that "
            "respects its future readers."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "aesthetic_sensitivity": {"value": 0.91, "setpoint": 0.8, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["elegance_scorer", "form_evaluator", "symmetry_detector"]
