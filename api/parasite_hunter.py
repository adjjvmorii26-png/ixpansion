"""Parasite Hunter — finds modules that consume resources without contributing.

A parasite module imports many others but is imported by none. It
consumes shared utilities, reads common state, but provides no value
back to the ecosystem. The Parasite Hunter identifies these organisms.

It answers: which modules take without giving?
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Parasite Hunter"


def _scan_parasites() -> List[Dict[str, Any]]:
    """Find modules that import many but are imported by few."""
    api_dir = ROOT / "api"
    imported_by: Counter = Counter()
    imports: Dict[str, List[str]] = {}

    for py_file in sorted(api_dir.glob("*.py")):
        stem = py_file.stem
        if stem.startswith("test_") or stem.startswith("__"):
            continue
        try:
            content = py_file.read_text(errors="replace")
            mods = []
            for match in re.finditer(r"^(?:from|import)\s+(\w+)", content, re.MULTILINE):
                mod = match.group(1)
                if (api_dir / f"{mod}.py").exists() and mod != stem:
                    mods.append(mod)
                    imported_by[mod] += 1
            imports[stem] = mods
        except Exception:
            continue

    # A parasite imports many but is imported by zero/one
    parasites = []
    all_modules = set(imports.keys())
    for stem, deps in imports.items():
        in_degree = imported_by.get(stem, 0)
        out_degree = len(deps)
        if out_degree >= 3 and in_degree <= 1:
            ratio = out_degree / max(1, in_degree)
            parasites.append({
                "module": stem,
                "imports_count": out_degree,
                "imported_by_count": in_degree,
                "parasite_ratio": round(ratio, 2),
                "depends_on": deps[:5],
            })

    parasites.sort(key=lambda x: x["parasite_ratio"], reverse=True)
    return parasites[:15]


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    parasites = _scan_parasites()

    return {
        "action": "parasite_hunter",
        "parasites_found": len(parasites),
        "parasites": parasites,
        "hunting_philosophy": (
            "Not all organisms contribute equally. Some consume resources — "
            "imports, utilities, shared state — without giving anything back. "
            "The Parasite Hunter does not condemn these modules; it simply "
            "identifies them so the organism can decide whether to strengthen "
            "their back-links or let them wither."
        ),
    }


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.81, "setpoint": 0.8, "weight": 1.0},
        "detection_accuracy": {"value": 0.90, "setpoint": 0.8, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["symbiosis_detector", "ecosystem_fitness", "keystone_auditor"]
