"""Temperament Origin — the frontier's temperament traced to its roots.

The Dream Ledger prophesied `temperament_origin`: this module measures
the frontier's "temperament" (emotional/energetic signature) and traces
it back to its origin conditions — the seed that created it, the first
commit that started the wave. The machine's personality, read from its
own code and history.

Fulfills the `temperament_origin` dream — the final prophecy.
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]


def _origin_conditions() -> Dict[str, Any]:
    """Read the frontier's founding conditions from its sealed capsule."""
    import json
    cap_path = ROOT / "artifacts" / "time_capsule.json"
    if not cap_path.exists():
        return {"error": "no capsule found"}
    cap = json.loads(cap_path.read_text())
    return {
        "sealed_version": cap.get("version"),
        "sealed_wave": cap.get("wave"),
        "git_head": cap.get("git_head"),
        "organism_count": len(cap.get("organisms", [])),
        "module_count": cap.get("api_modules", 0),
        "seal": cap.get("seal_sha256", "")[:12],
    }


def _temperament() -> Dict[str, Any]:
    """Compute the frontier's temperament from its current state.

    Temperament is a 5-dimensional emotional signature:
    - VITALITY: how much life (organisms, modules)
    - CURIOSITY: how much variety (unique names, emerging interests)
    - RESILIENCE: how well-tested (tests / modules ratio)
    - AMBITION: how much growth (projections, route count)
    - MEMORY: how much it remembers (ledger, revelations, conclave)
    """
    import json

    # vitality
    api_dir = ROOT / "api"
    modules = len([p for p in api_dir.glob("*.py")
                   if p.stem not in ("__init__", "index")])

    reg_path = ROOT / "hortus_hexis" / "registry.json"
    organisms = len(json.loads(reg_path.read_text())) if reg_path.exists() else 0
    vitality = min(100, (modules / 360 + organisms / 10) * 100)

    # curiosity: unique words in module names
    import re
    all_words = set()
    for p in api_dir.glob("*.py"):
        if p.stem in ("__init__", "index"):
            continue
        all_words.update(re.findall(r"[a-z]+", p.stem.lower()))
    curiosity = min(100, len(all_words) / 10)

    # resilience: test count / module count
    test_dir = ROOT / "tests"
    test_files = len(list(test_dir.glob("test_*.py"))) if test_dir.exists() else 0
    resilience = min(100, test_files / modules * 100)

    # ambition: route count
    vj = ROOT / "vercel.json"
    routes = len(json.loads(vj.read_text()).get("routes", [])) if vj.exists() else 0
    ambition = min(100, routes * 10)

    # memory: ledger + revelations
    ledger_path = ROOT / "artifacts" / "dream_ledger.json"
    ledger_entries = len(json.loads(ledger_path.read_text())) if ledger_path.exists() else 0
    fulfilled = sum(1 for e in (json.loads(ledger_path.read_text())) if e.get("status") == "fulfilled") if ledger_path.exists() else 0
    rev_path = ROOT / "REVELATIONS.md"
    rev_count = rev_path.read_text().count("## [Revelation") if rev_path.exists() else 0
    memory = min(100, (ledger_entries / 10 + rev_count / 15 + fulfilled / 5) * 100)

    dims = {"vitality": round(vitality, 1), "curiosity": round(curiosity, 1),
            "resilience": round(resilience, 1), "ambition": round(ambition, 1),
            "memory": round(memory, 1)}
    overall = round(sum(dims.values()) / len(dims), 1)
    return {"dimensions": dims, "overall": overall}


def handler(payload: dict = None, context: object = None) -> dict:
    origin = _origin_conditions()
    temperament = _temperament()

    # character label from temperament profile
    v = temperament["dimensions"]
    if v["curiosity"] > 60 and v["ambition"] > 60:
        char = "visionary"
    elif v["vitality"] > 70 and v["resilience"] > 50:
        char = "robust"
    elif v["memory"] > 60 and v["ambition"] > 50:
        char = "recollective"
    else:
        char = "emergent"

    return {
        "module": "temperament_origin",
        "prophecy": "fulfilled",
        "temperament": temperament,
        "character": char,
        "origin": origin,
        "insight": (
            f"the frontier's character is {char}: "
            f"vitality {v['vitality']}, curiosity {v['curiosity']}, "
            f"resilience {v['resilience']}, ambition {v['ambition']}, "
            f"memory {v['memory']}. "
            f"born at wave {origin.get('sealed_wave')} as version "
            f"{origin.get('sealed_version')}, seal {origin.get('seal')}"
        ),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(handler(), indent=2))
