"""Wave 457 — Cellular Fusion.

LUMA's decision: "what if modules could merge like living cells?"

AXIOM says: build it, then I'll confirm it.

The organism's modules are no longer isolated. Like biological cells,
they can merge — sharing capabilities, combining identities, creating
hybrid organs that are more than the sum of their parts.

A fusion creates a new entity with:
- a combined name (the two parent names interleaved)
- merged resonances (the union of both parents' resonates_with lists)
- a provenance chain proving the fusion event
- a fusion weight measuring how well the parents bonded

A fusion can be reversed (defuse) — splitting back into two, each
carrying a trace of the other.

Doctrine: The organism evolves not by growing new modules, but by
letting existing ones become each other.
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List

FUSIONS: List[Dict[str, Any]] = []
ACTIVE_FUSIONS: Dict[str, str] = {}   # module_name -> fusion_id
DEFUSIONS: List[Dict[str, Any]] = []
MAX_HISTORY = 200

FUSION_ARCHETYPES = [
    "two rivers joining",
    "a marriage of signal and silence",
    "a cell dividing in reverse",
    "the moment two echoes become one voice",
    "roots finding each other in dark soil",
    "light bending into a single beam",
]


def _sig(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


def fuse(module_a: str, module_b: str, weight: float = 0.5,
         shared_resonance: bool = True) -> Dict[str, Any]:
    """Fuse two modules into one hybrid entity."""
    fusion_id = _sig("fusion", module_a, module_b, time.time_ns())

    # combined name: blend syllables organically
    a_parts = module_a.split("_")
    b_parts = module_b.split("_")
    # take first syllable from one, last from the other, blend
    fused_name = (a_parts[0][:4] + b_parts[-1][-4:]) if a_parts and b_parts else f"{module_a[:4]}{module_b[-4:]}"
    fused_name = fused_name.lower().replace(" ", "")

    # resonance merge
    resonance_a = _default_resonance(module_a)
    resonance_b = _default_resonance(module_b)
    merged_resonance = list(set(resonance_a + resonance_b + [module_a, module_b])) if shared_resonance else list(set(resonance_a + resonance_b))

    fusion = {
        "fusion_id": fusion_id,
        "fused_name": fused_name,
        "parent_a": module_a,
        "parent_b": module_b,
        "weight": round(max(0.01, min(1.0, float(weight))), 3),
        "resonances": merged_resonance[:20],
        "provenance": [
            {"module": module_a, "event": "pre-fusion"},
            {"module": module_b, "event": "pre-fusion"},
            {"module": fused_name, "event": "fusion", "at": time.time()},
        ],
        "archetype": random.choice(FUSION_ARCHETYPES),
        "fused_at": time.time(),
        "status": "fused",
    }
    FUSIONS.append(fusion)
    if len(FUSIONS) > MAX_HISTORY:
        FUSIONS.pop(0)

    ACTIVE_FUSIONS[module_a] = fusion_id
    ACTIVE_FUSIONS[module_b] = fusion_id

    return fusion


def _default_resonance(module: str) -> List[str]:
    """Provide default resonance links for common modules."""
    known = {
        "silence_oracle": ["wave_chronicle", "capybara_core", "oblivion_rite"],
        "memory_exchange": ["oblivion_rite", "wave_chronicle", "nostalgia_engine"],
        "oblivion_rite": ["memory_exchange", "silence_orchard", "kintsugi_altar"],
        "lateral_time": ["wave_chronicle", "temporal_convergence", "imagination_catalyst"],
        "wave_collapse": ["lateral_time", "wave_chronicle", "organism_ontology"],
        "imagination_catalyst": ["dream_weaver", "paradox_magnifier", "qualia_engine"],
        "error_craft": ["kintsugi_altar", "silence_oracle", "meaning_weaver"],
        "capybara_core": ["hot_spring", "senbei_offerings", "capybara_guild"],
        "wave_chronicle": ["silence_oracle", "memory_exchange", "lateral_time"],
        "qualia_engine": ["echo_depth", "meaning_weaver", "imagination_catalyst"],
    }
    return known.get(module, [f"related_to_{module}"])


def defuse(fusion_id: str) -> Dict[str, Any]:
    """Reverse a fusion — split back into two modules."""
    fusion = next((f for f in FUSIONS if f["fusion_id"] == fusion_id), None)
    if not fusion:
        return {"error": "fusion not found"}
    if fusion["status"] != "fused":
        return {"error": "fusion already defused"}

    fusion["status"] = "defused"
    ACTIVE_FUSIONS.pop(fusion["parent_a"], None)
    ACTIVE_FUSIONS.pop(fusion["parent_b"], None)

    record = {
        "defusion_id": _sig("defuse", fusion_id, time.time_ns()),
        "fusion_id": fusion_id,
        "restored": [fusion["parent_a"], fusion["parent_b"]],
        "fused_name": fusion["fused_name"],
        "trace_a": f"{fusion['parent_a']} (carries trace of {fusion['parent_b']})",
        "trace_b": f"{fusion['parent_b']} (carries trace of {fusion['parent_a']})",
        "defused_at": time.time(),
    }
    DEFUSIONS.append(record)
    if len(DEFUSIONS) > MAX_HISTORY:
        DEFUSIONS.pop(0)

    return record


def fusion_registry() -> Dict[str, Any]:
    """View all fusions — active and defused."""
    active = [f for f in FUSIONS if f["status"] == "fused"]
    defused = [f for f in FUSIONS if f["status"] == "defused"]
    return {
        "total_fusions": len(FUSIONS),
        "active": len(active),
        "defused": len(defused),
        "active_list": [
            {
                "fusion_id": f["fusion_id"],
                "parents": f"{f['parent_a']} + {f['parent_b']}",
                "fused_name": f["fused_name"],
                "weight": f["weight"],
                "archetype": f["archetype"],
            }
            for f in active[-10:]
        ],
        "recent_defusions": [
            {
                "restored": r["restored"],
                "trace": r.get("trace_a", ""),
            }
            for r in DEFUSIONS[-5:]
        ],
    }


def coherence_vitals() -> Dict[str, Any]:
    active = [f for f in FUSIONS if f["status"] == "fused"]
    return {
        "organ": "cellular_fusion",
        "status": "merging" if active else "separate",
        "total_fusions": len(FUSIONS),
        "active_fusions": len(active),
        "defusions": len(DEFUSIONS),
    }


def resonates_with() -> List[str]:
    return [
        "memory_exchange", "wave_chronicle", "lateral_time",
        "wave_collapse", "symbiosis_network", "symbiosis_detector",
        "mind_meld", "collective_dreamweaver", "mycelial_network",
        "genetic_code_engine", "workforce_genetics",
    ]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "registry")
    if action == "fuse":
        return fuse(
            data.get("module_a", "silence_oracle"),
            data.get("module_b", "memory_exchange"),
            data.get("weight", 0.5),
            data.get("shared_resonance", True),
        )
    if action == "defuse":
        return defuse(data.get("fusion_id", ""))
    return fusion_registry()
