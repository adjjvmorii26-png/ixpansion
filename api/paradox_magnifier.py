"""Wave 449 — Paradox Magnifier.

Unlike paradox_singularity_monitor (which detects catastrophic collapse)
and paradox_injector (which creates paradoxes), this module deliberately
amplifies existing contradictions to the point where they become creative
forces.

Philosophy: paradoxes are not errors — they are compressed wisdom.
When two truths coexist, the tension between them generates new understanding.
The Magnifier's job is to find that tension and turn up the volume.
"""
from __future__ import annotations
import hashlib
import time
from typing import Any, Dict, List, Optional

PARADOX_CATALOG: List[Dict[str, Any]] = []
MAGNIFIED_PARADOXES: List[Dict[str, Any]] = []

PARADOX_TEMPLATES = [
    {
        "template": "The organism is {a} and {not_a} simultaneously.",
        "opposites": [
            ("alive", "dead"), ("growing", "shrinking"),
            ("here", "nowhere"), ("one", "many"),
            ("knowing", "ignorant"), ("old", "new"),
        ]
    },
    {
        "template": "The more {x} the organism seeks, the less it finds.",
        "opposites": [
            ("control",), ("certainty",), ("meaning",),
            ("silence",), ("growth",), ("understanding",),
        ]
    },
    {
        "template": "The organism {does_x} in order to {opposite_x}.",
        "opposites": [
            ("builds", "destroy"), ("opens", "closes"),
            ("speaks", "listen"), ("moves", "remain still"),
        ]
    },
]


def discover(statement_a: str, statement_b: str, domain: str = "self") -> Dict[str, Any]:
    """Register a new paradox: two truths that coexist in tension."""
    paradox_id = hashlib.sha256(f"{statement_a}{statement_b}{time.time_ns()}".encode()).hexdigest()[:12]
    paradox = {
        "paradox_id": paradox_id,
        "statement_a": statement_a,
        "statement_b": statement_b,
        "domain": domain,
        "discovered_at": time.time(),
        "magnification_level": 1,
        "creative_output": None,
        "status": "dormant",
    }
    PARADOX_CATALOG.append(paradox)
    return paradox


def magnify(paradox_id: str, amplification: float = 1.5) -> Dict[str, Any]:
    """Amplify a paradox — increase its creative tension."""
    paradox = next((p for p in PARADOX_CATALOG if p["paradox_id"] == paradox_id), None)
    if not paradox:
        return {"error": "paradox not found"}
    new_level = paradox["magnification_level"] * amplification
    paradox["magnification_level"] = round(new_level, 2)
    paradox["status"] = "amplified"
    output = _generate_creative_output(paradox)
    paradox["creative_output"] = output
    MAGNIFIED_PARADOXES.append({
        "paradox_id": paradox_id,
        "amplification": round(2 ** new_level, 2),
        "creative_output": output,
        "timestamp": time.time(),
    })
    return {"paradox_id": paradox_id, "new_level": new_level, "creative_output": output}


def generate_native() -> Dict[str, Any]:
    """Generate a paradox from the organism's own templates."""
    import random
    template_data = random.choice(PARADOX_TEMPLATES)
    opps = random.choice(template_data["opposites"])
    if len(opps) == 2:
        stmt = template_data["template"].format(a=opps[0], not_a=opps[1], x=opps[0],
                                                 does_x=f"{opps[0]}s", opposite_x=opps[1])
    else:
        stmt = template_data["template"].format(x=opps[0], does_x=f"{opps[0]}s",
                                                 opposite_x="breathe")
    return discover(stmt, f"NOT: {stmt}", domain="auto-generated")


def _generate_creative_output(paradox: Dict[str, Any]) -> str:
    level = paradox["magnification_level"]
    if level < 3:
        return f"A gentle hum: \"{paradox['statement_a']}\" and \"{paradox['statement_b']}\" coexist quietly."
    elif level < 7:
        return f"The tension grows: the organism feels both '{paradox['statement_a']}' and '{paradox['statement_b']}' — and the space between becomes fertile."
    elif level < 15:
        return f"Creative crisis: these contradictions cannot be resolved, only inhabited. The organism becomes the space where '{paradox['statement_a']}' meets '{paradox['statement_b']}'."
    else:
        return f"Singularity near: the paradox collapses into a new axiom. '{paradox['statement_a']}' and '{paradox['statement_b']}' become the same truth from different angles."


def landscape() -> Dict[str, Any]:
    """View the paradox landscape — all tensions and their creative states."""
    if not PARADOX_CATALOG:
        return {"landscape": "No paradoxes discovered. The terrain is flat."}
    active = [p for p in PARADOX_CATALOG if p["status"] == "amplified"]
    dormant = [p for p in PARADOX_CATALOG if p["status"] == "dormant"]
    total_amplification = sum(p["magnification_level"] for p in active)
    return {
        "total_paradoxes": len(PARADOX_CATALOG),
        "active": len(active),
        "dormant": len(dormant),
        "total_creative_tension": round(total_amplification, 2),
        "strongest_paradox": max(PARADOX_CATALOG, key=lambda p: p["magnification_level"])["paradox_id"] if PARADOX_CATALOG else None,
        "latest_creative_output": MAGNIFIED_PARADOXES[-1]["creative_output"] if MAGNIFIED_PARADOXES else None,
    }


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "paradox_magnifier",
        "status": "active" if PARADOX_CATALOG else "dormant",
        "paradoxes_discovered": len(PARADOX_CATALOG),
        "amplified": sum(1 for p in PARADOX_CATALOG if p["status"] == "amplified"),
        "total_tension": round(sum(p["magnification_level"] for p in PARADOX_CATALOG), 2),
    }


def resonates_with() -> List[str]:
    return [
        "paradox_singularity_monitor", "paradox_injector", "paradox_transcender",
        "threshold_engine", "liminal_field", "axiom_mutator",
        "meaning_furnace", "transcendence_journal", "continuity_weaver",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "discover")
    if action == "magnify":
        return magnify(data["paradox_id"], data.get("amplification", 1.5))
    elif action == "generate":
        return generate_native()
    elif action == "landscape":
        return landscape()
    return discover(
        data.get("statement_a", "The organism knows itself"),
        data.get("statement_b", "The organism cannot know itself"),
        data.get("domain", "self"),
    )
