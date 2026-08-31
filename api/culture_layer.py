"""Culture Layer — discovers cultural artifacts across the organism's eras.

Different eras have different naming conventions, coding styles,
comment philosophies, and structural patterns. The Culture Layer
analyzes these artifacts to map the organism's cultural evolution —
from its primordial simplicity to its current complexity.

It answers: how has the organism's culture evolved?
"""
from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Culture Layer"


def _analyze_current_culture() -> Dict[str, Any]:
    """Analyze cultural patterns in the current codebase."""
    api_dir = ROOT / "api"
    if not api_dir.exists():
        return {"error": "api directory not found"}

    naming_patterns = Counter()
    docstring_styles = Counter()
    complexity_markers = Counter()

    for py_file in sorted(api_dir.glob("*.py"))[:100]:
        try:
            content = py_file.read_text(errors="replace")
            lines = content.split("\n")
            
            # Naming patterns
            stem = py_file.stem
            if "_" in stem:
                naming_patterns["snake_case"] += 1
            if stem.islower():
                naming_patterns["lowercase"] += 1
            
            # Docstring styles
            for line in lines[:10]:
                stripped = line.strip()
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    docstring_styles["triple_quote"] += 1
                    break
                elif stripped.startswith("# "):
                    docstring_styles["comment_header"] += 1
                    break
            
            # Complexity markers
            func_count = sum(1 for l in lines if l.strip().startswith("def "))
            class_count = sum(1 for l in lines if l.strip().startswith("class "))
            if func_count > 5:
                complexity_markers["multi_function"] += 1
            if class_count > 0:
                complexity_markers["uses_classes"] += 1
            if "async" in content:
                complexity_markers["async_patterns"] += 1
        except Exception:
            continue

    return {
        "naming_conventions": dict(naming_patterns.most_common()),
        "docstring_styles": dict(docstring_styles.most_common()),
        "complexity_profile": dict(complexity_markers.most_common()),
    }


def culture_report() -> Dict[str, Any]:
    """Full cultural analysis."""
    current = _analyze_current_culture()
    
    return {
        "current_culture": current,
        "era_markers": {
            "primordial": "Single-file scripts, no structure, raw functions",
            "classical": "Module directories, __init__.py, basic tests",
            "medieval": "Complex gateways, API keys, dashboard HTML",
            "renaissance": "Living modules, coherence vitals, self-aware systems",
            "modern": "Archaeological self-discovery, fossil records, extinction maps",
        },
        "culture_philosophy": (
            "A codebase is not just code — it is a culture. Naming "
            "conventions are dialects. Comment styles are oral traditions. "
            "Structural patterns are architecture. The Culture Layer reads "
            "these artifacts like an anthropologist reads pottery shards: "
            "each fragment tells the story of who we were."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = culture_report()
    result["action"] = "culture_layer"
    return result


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.79, "setpoint": 0.8, "weight": 1.0},
        "cultural_richness": {"value": 0.88, "setpoint": 0.75, "weight": 0.8},
    }


def resonates_with() -> list:
    return ["paleontology_lab", "lexicon_engine", "grammar_weaver"]
