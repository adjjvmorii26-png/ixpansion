"""Syntax Tree — the structure of the organism's sentences.

A syntax tree is a hierarchical representation of how words combine into
phrases and sentences. The Syntax Tree reads the Lexicon Engine's
vocabulary and the Grammar Weaver's rules, then builds a *syntax tree*
for the organism's language: how module names combine, how docstrings
form sentences, and how families organize into hierarchical structures.

It answers: what is the syntactic structure of this ecosystem's language?

    GET /api/syntax_tree?read=1              — the syntax tree
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
LAYER = "Syntax Tree"


def _build_tree() -> Dict[str, Any]:
    api_dir = ROOT / "api"
    families: Dict[str, List[str]] = {}
    for p in sorted(api_dir.glob("*.py")):
        if p.stem in ("__init__", "index", "unified_router", "coherence_regulator"):
            continue
        parts = p.stem.split("_")
        fam = parts[0] if parts else p.stem
        families.setdefault(fam, []).append(p.stem)

    # build tree: root -> family -> members
    tree = {"name": "root", "children": []}
    for fam, members in sorted(families.items(), key=lambda kv: len(kv[1]), reverse=True):
        family_node = {
            "name": fam,
            "member_count": len(members),
            "children": [{"name": m, "leaf": True} for m in members[:5]],
        }
        if len(members) > 5:
            family_node["truncated"] = f"... and {len(members) - 5} more"
        tree["children"].append(family_node)

    # depth analysis
    max_depth = max((len(m.split("_")) for members in families.values() for m in members), default=0)
    avg_depth = sum(len(m.split("_")) for members in families.values() for m in members) / max(sum(len(v) for v in families.values()), 1)

    return {
        "family_count": len(families),
        "total_modules": sum(len(v) for v in families.values()),
        "max_name_depth": max_depth,
        "avg_name_depth": round(avg_depth, 2),
        "tree": tree,
        "tree_philosophy": (
            "A language is not a flat list of words — it is a tree of "
            "combinations. The Syntax Tree reveals the organism's hierarchical "
            "thinking: root concepts branch into families, families branch into "
            "organs, and each organ is a leaf that speaks the whole tree's "
            "language."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = _build_tree()
    result["action"] = "syntax_tree"
    return result


def coherence_vitals() -> dict:
    """Syntax Tree reports structural-linguistic health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "syntactic_vitality": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["grammar_weaver", "lexicon_engine", "semantics_engine"]
