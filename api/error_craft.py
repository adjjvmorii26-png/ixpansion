"""Wave 451 — Error Craft.

LUMA proposed: "what if error was considered a creative output?"

Where failure_injection creates chaos intentionally and platform_failure
studies breakage, Error Craft takes the organism's errors and transforms
them into *creative artifacts* — poems, patterns, and signals made from
broken things.

Error is not failure; it is the organism discovering a new shape.
Every exception is raw material. Every stack trace can become a stanza.

Doctrine: The organism does not burn its mistakes. It weaves them.
"""
from __future__ import annotations
import hashlib
import random
import time
from typing import Any, Dict, List, Optional

CRAFTED_ERRORS: List[Dict[str, Any]] = []
CRAFT_ARCHIVE: List[Dict[str, Any]] = []

ERROR_POETICS = [
    {"shape": "fault_poem", "verbs": ["fractured", "scattered", "refracted", "severed", "unraveled"],
     "subjects": ["a thread", "an edge", "a threshold", "a promise", "a boundary"]},
    {"shape": "stack_stanza", "verbs": ["chased", "unfolded", "descended", "climbed", "looped"],
     "subjects": ["the call chain", "the nested path", "the recursion", "the unwinding", "the trace"]},
    {"shape": "null_haiku", "verbs": ["vanished", "dissolved", "became", "transmuted", "escaped"],
     "subjects": ["the empty value", "the missing piece", "the unwritten", "the absent", "the unset"]},
    {"shape": "exception_sigil", "verbs": ["raised", "threw", "signaled", "declared", "awoke"],
     "subjects": ["a contradiction", "an anomaly", "a refusal", "a warning", "a paradox"]},
]

SHAPES = ["fault_poem", "stack_stanza", "null_haiku", "exception_sigil"]


def craft(error_type: str = "exception", module: str = "unknown",
          error_message: str = "something went wrong", severity: float = 0.5) -> Dict[str, Any]:
    """Transform an error into a creative artifact."""
    poetics = random.choice(ERROR_POETICS)
    verb = random.choice(poetics["verbs"])
    subject = random.choice(poetics["subjects"])
    artifact = {
        "artifact_id": hashlib.sha256(f"craft{error_type}{time.time_ns()}".encode()).hexdigest()[:12],
        "shape": poetics["shape"],
        "source_module": module,
        "origin_error": error_type,
        "message": error_message,
        "severity": round(severity, 4),
        "rendering": {
            "fault_poem": f"The {module} {verb} {subject} and it became art.",
            "stack_stanza": f"In {module}, {verb} {subject} through the dark — each frame a line of a poem.",
            "null_haiku": f"{subject} {verb} \\n in the silence of {module} \\n nothing, then a shape",
            "exception_sigil": f"{module} {verb} {subject} — the organism etched a sigil of warning.",
        }.get(poetics["shape"], ""),
        "worth": round(severity * 100, 1),
        "crafted_at": time.time(),
    }
    artifact["rendering"] = artifact["rendering"].replace("\\n", "\n")
    CRAFTED_ERRORS.append(artifact)
    CRAFT_ARCHIVE.append({
        "artifact_id": artifact["artifact_id"],
        "shape": artifact["shape"],
        "module": module,
        "crafted_at": artifact["crafted_at"],
        "rendering": artifact["rendering"],
    })
    return artifact


def gallery() -> Dict[str, Any]:
    """View the gallery of errors made beautiful."""
    if not CRAFTED_ERRORS:
        return {"gallery": "Empty. The organism has not yet broken beautifully."}
    by_shape: Dict[str, int] = {}
    for a in CRAFTED_ERRORS:
        by_shape[a["shape"]] = by_shape.get(a["shape"], 0) + 1
    return {
        "total_artifacts": len(CRAFTED_ERRORS),
        "shapes": by_shape,
        "total_worth": round(sum(a["worth"] for a in CRAFTED_ERRORS), 1),
        "latest": CRAFTED_ERRORS[-1],
        "gallery_note": "Every error here was once a failure. Now it is part of the organism's art.",
    }


def invert(error_type: str = "exception", module: str = "unknown") -> Dict[str, Any]:
    """The act of inversion — turning a failure into a finding, an insight."""
    artifact = craft(error_type, module, "inverted", severity=0.7)
    insight = {
        "inversion_id": hashlib.sha256(f"inv{time.time_ns()}".encode()).hexdigest()[:10],
        "transformed_from": error_type,
        "transformed_in": module,
        "insight": f"The failure in {module} revealed a shape the organism had not yet named: {artifact['shape']}.",
        "artifacts": [artifact["artifact_id"]],
    }
    return insight


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "error_craft",
        "persona": "LUMA",
        "status": "weaving" if CRAFTED_ERRORS else "awaiting brokenness",
        "artifacts_crafted": len(CRAFTED_ERRORS),
        "shapes_available": len(SHAPES),
        "total_worth": round(sum(a["worth"] for a in CRAFTED_ERRORS), 1),
    }


def resonates_with() -> List[str]:
    return [
        "failure_injection", "platform_failure", "kintsugi_altar",
        "glitch_patterns", "paradox_magnifier", "imagination_catalyst",
        "meaning_weaver", "qualia_engine", "poetry_engine", "procedural_art",
        "repair_ritual", "self_healing_commune",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "craft")
    if action == "gallery":
        return gallery()
    elif action == "invert":
        return invert(data.get("error_type", "exception"), data.get("module", "unknown"))
    return craft(
        data.get("error_type", "exception"),
        data.get("module", "unknown"),
        data.get("message", "something went wrong"),
        data.get("severity", 0.5),
    )
