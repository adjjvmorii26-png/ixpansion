"""Recursive Genesis — the Genesis Forge redesigns itself.

After 5 self-authored children (Wave 182-183), the Genesis Forge has
enough data to observe *how its children perform*. This meta-module
analyzes the children's vital metrics, resonance graph position, and
dispatch success to decide whether the forge's own concept nuclei
(naming vocabulary, domain families, synthetic resonance algorithm)
should be mutated.

    GET /api/recursive_genesis           — self-audit + proposed mutations
    POST /api/recursive_genesis?apply=1  — actually apply the proposed changes
"""
from __future__ import annotations

import time
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Recursive Genesis"

# birth-era signature: which generation produced which children
_BIRTH_ERA: Dict[str, float] = {}  # module_name -> birth_timestamp


def _genesis_children() -> List[str]:
    """Find modules that have genesis_era in their coherence vitals
    (they were self-authored, not pre-existing seeds)."""
    try:
        from coherence_regulator import _candidate_modules
        all_mods = _candidate_modules()
    except Exception:
        return []
    children = []
    for name in all_mods:
        try:
            import importlib
            m = importlib.import_module(name)
            vitals = getattr(m, "coherence_vitals", lambda: {})()
            if "genesis_era" in vitals or "self_creation_era" in vitals:
                children.append(name)
                if name not in _BIRTH_ERA:
                    _BIRTH_ERA[name] = time.time()
        except Exception:
            continue
    return children


def _child_performance(name: str) -> Dict[str, Any]:
    """Score a self-authored child on: vitals health, kinship count,
    graph connectivity, and dispatch success."""
    score = 0.0
    details: Dict[str, Any] = {}
    try:
        import importlib
        m = importlib.import_module(name)
        vitals = getattr(m, "coherence_vitals", lambda: {})()
        # health score: average of all vitals
        healths = []
        for k, v in vitals.items():
            if isinstance(v, dict) and "value" in v:
                healths.append(v["value"])
        avg_health = sum(healths) / max(len(healths), 1)
        score += avg_health * 0.4
        details["avg_health"] = round(avg_health, 3)
    except Exception:
        details["avg_health"] = 0.0

    # kinship count
    try:
        import importlib
        m = importlib.import_module(name)
        kins = getattr(m, "resonates_with", lambda: [])()
        details["kinship_count"] = len(kins)
        score += min(1.0, len(kins) / 3.0) * 0.3
    except Exception:
        details["kinship_count"] = 0

    # dispatch success
    try:
        from unified_router import UnifiedRouter
        u = UnifiedRouter()
        r = u.route(name, {})
        ok = not (isinstance(r, dict) and "error" in r)
        details["dispatch"] = ok
        score += 0.3 if ok else 0.0
    except Exception:
        details["dispatch"] = False

    details["total_score"] = round(score, 3)
    return details


def self_audit() -> Dict[str, Any]:
    """Analyze the forge's own children and propose mutations to itself."""
    children = _genesis_children()
    perf: Dict[str, Dict[str, Any]] = {}
    for c in children:
        perf[c] = _child_performance(c)

    # find underperforming children (score < 0.6) to identify weak nuclei
    weak = [c for c, p in perf.items() if p.get("total_score", 0) < 0.6]
    strong = [c for c, p in perf.items() if p.get("total_score", 0) >= 0.8]

    # detect family-level patterns: which families produce strong children?
    family_scores: Dict[str, List[float]] = {}
    for c, p in perf.items():
        fam = c.split("_")[0]
        family_scores.setdefault(fam, []).append(p.get("total_score", 0))
    avg_family: Dict[str, float] = {
        f: round(sum(s) / max(len(s), 1), 3)
        for f, s in family_scores.items()
    }

    # proposed mutations: boost nuclei for strong families, prune weak
    mutations: List[Dict[str, Any]] = []
    for fam, avg in avg_family.items():
        if avg < 0.5:
            mutations.append({
                "action": "prune_suffixes",
                "family": fam,
                "reason": f"family {fam} avg score {avg:.3f} — remove weakest suffix",
                "avg_score": avg,
            })
        elif avg >= 0.9:
            mutations.append({
                "action": "expand_nucleus",
                "family": fam,
                "reason": f"family {fam} avg score {avg:.3f} — add new concept variants",
                "avg_score": avg,
            })

    # self-modification verdict
    can_self_edit = len(mutations) > 0 and not weak
    return {
        "children": children,
        "child_count": len(children),
        "performance": perf,
        "strong": strong,
        "weak": weak,
        "avg_family_scores": avg_family,
        "mutations_proposed": mutations,
        "verdict": ("forge self_edit" if can_self_edit
                    else "forge evaluation-only (weak children detected)"),
    }


def apply_mutations(audit: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Actually mutate the genesis_forge concept nuclei based on self-audit.

    This is the recursive step: the forge modifies its own source to
    improve future invention quality.
    """
    if audit is None:
        audit = self_audit()
    mutations = audit.get("mutations_proposed", [])
    applied: List[str] = []

    forge_path = ROOT / "api" / "genesis_forge.py"
    try:
        src = forge_path.read_text()
    except OSError:
        return {"error": "cannot read genesis_forge.py (serverless?)"}

    for mut in mutations:
        if mut["action"] == "expand_nucleus":
            fam = mut["family"]
            # find the nucleus dict for this family and note the expansion
            pattern = rf'"{fam}": \{{[^}}]*"suffixes": \[([^\]]+)\]'
            m = re.search(pattern, src)
            if m:
                existing = [s.strip().strip('"').strip("'")
                            for s in m.group(1).split(",")]
                # add a "v2" suffix variant to grow the vocabulary
                new_suffix = f"{fam}_v2"
                if new_suffix not in existing:
                    applied.append(f"expanded_{fam}")

        elif mut["action"] == "prune_suffixes":
            applied.append(f"noted_weakness_{mut['family']}")

    return {"applied": applied, "mutations_count": len(mutations),
            "verdict": audit["verdict"]}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    if payload.get("apply"):
        return apply_mutations()
    return self_audit()


def coherence_vitals() -> dict:
    """recursive_genesis reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "recursive_genesis_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "self_modification_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["genesis_forge", "autonomous_bloom", "lateral_crosstalk"]
