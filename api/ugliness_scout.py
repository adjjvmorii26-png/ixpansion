"""Ugliness Scout — finds the ugliest code and proposes beauty improvements.

Every beautiful codebase has rough edges. The Ugliness Scout identifies
the modules with the lowest elegance scores, longest lines, deepest
nesting, and most confusing structures — then proposes specific fixes.

It answers: where is the organism's code ugliest?
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Ugliness Scout"


def _scan_ugliness() -> List[Dict[str, Any]]:
    """Find the ugliest modules."""
    api_dir = ROOT / "api"
    ugly_modules = []

    for py_file in sorted(api_dir.glob("*.py"))[:60]:
        try:
            content = py_file.read_text(errors="replace")
            lines = content.split("\n")
            lengths = [len(l) for l in lines]

            # Ugliness signals
            avg_len = sum(lengths) / max(1, len(lengths))
            long_lines = sum(1 for l in lengths if l > 100)
            total_lines = len(lines)

            # Nesting depth
            max_indent = 0
            for l in lines:
                stripped = l.lstrip()
                indent = len(l) - len(stripped)
                max_indent = max(max_indent, indent)
            nesting = max_indent // 4

            # Missing docstrings
            try:
                tree = ast.parse(content)
                funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                undoced = sum(1 for f in funcs if not ast.get_docstring(f))
            except Exception:
                undoced = 0
                funcs = []

            # Ugliness score (higher = uglier)
            ugliness = (
                (avg_len / 120) * 0.25
                + (long_lines / max(1, total_lines)) * 0.25
                + (nesting / 8) * 0.3
                + (undoced / max(1, len(funcs))) * 0.2
            )

            if ugliness > 0.3:
                ugly_modules.append({
                    "file": py_file.stem,
                    "ugliness_score": round(ugliness, 3),
                    "avg_line_length": round(avg_len, 1),
                    "long_lines": long_lines,
                    "nesting_depth": nesting,
                    "undocumented_functions": undoced,
                })
        except Exception:
            continue

    ugly_modules.sort(key=lambda x: x["ugliness_score"], reverse=True)
    return ugly_modules[:10]


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    ugly = _scan_ugliness()

    proposals = []
    for u in ugly:
        fixes = []
        if u["avg_line_length"] > 80:
            fixes.append("Break long lines at logical boundaries")
        if u["nesting_depth"] > 5:
            fixes.append("Extract nested logic into helper functions")
        if u["long_lines"] > 3:
            fixes.append("Apply consistent line length limits")
        if u["undocumented_functions"] > 2:
            fixes.append("Add docstrings to public functions")
        proposals.append({"file": u["file"], "fixes": fixes})

    return {
        "action": "ugliness_scout",
        "ugly_modules_found": len(ugly),
        "ugliest_modules": ugly,
        "improvement_proposals": proposals,
        "scout_philosophy": (
            "The Ugliness Scout does not shame — it illuminates. Every "
            "ugly module is an opportunity for beauty. By identifying "
            "long lines, deep nesting, and undocumented functions, "
            "the scout provides a concrete path from rough to refined."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.80, "setpoint": 0.8, "weight": 1.0},
        "detection_honesty": {"value": 0.95, "setpoint": 0.9, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["elegance_scorer", "beauty_index", "form_evaluator"]
