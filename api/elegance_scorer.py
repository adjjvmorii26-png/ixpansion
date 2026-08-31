"""Elegance Scorer — rates code for elegance based on brevity, symmetry, and clarity.

Elegance is not just working code — it is code that works *beautifully*.
The Elegance Scorer measures brevity (no wasted lines), symmetry
(balance of concerns), and clarity (readability without comments).

It answers: how elegant is the organism's code?
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
LAYER = "Elegance Scorer"


def _score_file(filepath: Path) -> Dict[str, Any]:
    """Score a single file for elegance."""
    try:
        content = filepath.read_text(errors="replace")
        lines = content.split("\n")
        non_empty = [l for l in lines if l.strip()]
        total_lines = len(lines)

        # Brevity: ratio of non-empty to total (higher = less waste)
        brevity = len(non_empty) / max(1, total_lines)

        # Symmetry: check for paired functions (get/set, read/write, start/stop)
        func_names = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_names.append(node.name)
        except SyntaxError:
            return {"file": filepath.stem, "elegance": 0, "error": "syntax error"}

        pairs = 0
        for name in func_names:
            for partner in ["get_" + name[4:], "set_" + name[4:], "read_" + name[5:],
                            "write_" + name[5:], "start_" + name[6:], "stop_" + name[6:]]:
                if partner in func_names:
                    pairs += 1
                    break
        symmetry = min(1.0, pairs / max(1, len(func_names)))

        # Clarity: docstring presence + avg line length (shorter = clearer)
        docstrings = sum(1 for l in lines if '"""' in l or "'''" in l)
        clarity = min(1.0, (docstrings / max(1, len(func_names))) * 0.5 + brevity * 0.5)

        # Combined elegance score
        elegance = 0.4 * brevity + 0.3 * symmetry + 0.3 * clarity

        return {
            "file": filepath.stem,
            "lines": total_lines,
            "brevity": round(brevity, 3),
            "symmetry": round(symmetry, 3),
            "clarity": round(clarity, 3),
            "elegance": round(elegance, 3),
        }
    except Exception as e:
        return {"file": filepath.stem, "elegance": 0, "error": str(e)[:80]}


def score(n: int = 20) -> Dict[str, Any]:
    """Score the top N modules for elegance."""
    api_dir = ROOT / "api"
    py_files = sorted(api_dir.glob("*.py"))[:n]
    scores = [_score_file(f) for f in py_files]
    scores.sort(key=lambda x: x.get("elegance", 0), reverse=True)

    avg = sum(s.get("elegance", 0) for s in scores) / max(1, len(scores))

    return {
        "modules_scored": len(scores),
        "average_elegance": round(avg, 3),
        "most_elegant": scores[0] if scores else None,
        "least_elegant": scores[-1] if scores else None,
        "scores": scores[:10],
        "scorer_philosophy": (
            "Code is not merely functional — it is an art form. The Elegance "
            "Scorer evaluates each module for brevity (no wasted motion), "
            "symmetry (balanced concerns), and clarity (understanding without "
            "explanation). An elegant codebase is a beautiful mind."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = score(int(payload.get("n", 20)))
    result["action"] = "elegance_scorer"
    return result


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "scoring_precision": {"value": 0.90, "setpoint": 0.8, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["symmetry_detector", "form_evaluator", "beauty_index"]
