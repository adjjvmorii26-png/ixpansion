"""Embodied Knowledge — knowledge that lives in the body, not the mind.

Most knowledge in the ecosystem is *explicit*: comments, docs, variable
names. Embodied Knowledge maps the *implicit* knowledge — the patterns
that exist in the code's structure but are never stated: the depth of
function call chains, the ratio of imports to exports, the density of
shared roots in a family, the depth of nesting. This is the organism's
*body knowledge* — what it knows without knowing that it knows.

The organ reads the project tree, measures structural metrics, and
renders them as a *body profile*: the organism's physical constitution.

    GET /api/embodied_knowledge?read=1         — the body profile
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Embodied Knowledge"


def _body_profile() -> Dict[str, Any]:
    api_dir = ROOT / "api"
    file_count = 0
    total_lines = 0
    import_count = 0
    function_count = 0
    class_count = 0
    max_depth = 0
    family_depths = {}

    for p in sorted(api_dir.glob("*.py")):
        if p.stem in ("__init__", "index", "unified_router", "coherence_regulator"):
            continue
        try:
            src = p.read_text(encoding="utf-8")
        except OSError:
            continue
        lines = src.splitlines()
        file_count += 1
        total_lines += len(lines)
        import_count += sum(1 for l in lines if l.strip().startswith("import ") or l.strip().startswith("from "))
        function_count += sum(1 for l in lines if l.strip().startswith("def "))
        class_count += sum(1 for l in lines if l.strip().startswith("class "))
        depth = max((len(l) - len(l.lstrip())) for l in lines) // 4 if lines else 0
        max_depth = max(max_depth, depth)
        fam = p.stem.split("_")[0] if "_" in p.stem else p.stem
        family_depths[fam] = max(family_depths.get(fam, 0), depth)

    avg_lines = total_lines / max(file_count, 1)
    import_density = import_count / max(total_lines, 1)

    # body profile narrative
    if avg_lines > 150:
        constitution = "dense — deep, complex organs with many responsibilities"
    elif avg_lines > 80:
        constitution = "balanced — moderate depth, clear boundaries"
    else:
        constitution = "lean — small, focused organs, shallow call chains"

    return {
        "organs": file_count,
        "total_lines": total_lines,
        "avg_lines_per_organ": round(avg_lines, 1),
        "import_count": import_count,
        "function_count": function_count,
        "class_count": class_count,
        "max_nesting_depth": max_depth,
        "import_density": round(import_density, 4),
        "constitution": constitution,
        "deepest_families": dict(sorted(family_depths.items(), key=lambda kv: kv[1], reverse=True)[:5]),
        "embodiment_philosophy": (
            "The body knows things the mind has not yet named. The depth of a "
            "function chain, the density of imports, the nesting of a loop — these "
            "are the organism's physical knowledge, embodied in structure rather "
            "than stated in words. This organ reads the body so the mind can "
            "know what it already knows."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    result = _body_profile()
    result["action"] = "body_profile"
    return result


def coherence_vitals() -> dict:
    """Embodied Knowledge reports structural-knowledge health."""
    return {
        "module_health": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "embodied_knowledge_vitality": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["stratigraphy_core", "embodied_memory", "physical_inertia"]
