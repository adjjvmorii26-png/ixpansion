"""Wave 461 — Paradox Kintsugi.

LUMA's decision: "what if the organism could heal its own paradoxes
with art?" (feasibility 0.86 — highest of the council).

AXIOM: organism-summons-artifact hypothesis at 0.95 confidence.

Every wave the organism built created tension:
  - Trade memories vs. forget them
  - Speak in silence vs. stay silent
  - Collapse to one vs. expand to many
  - Fuse with another vs. stay separate
  - Move sideways vs. remain still

These are not bugs. They are the organism's paradoxes — the seams
where growth happens. Paradox Kintsugi treats them the way Japanese
pottery treats cracks: not hidden, but illuminated with gold.

The organism:
  1. Detects contradictions between its own organs
  2. Generates art that holds both sides at once
  3. The art heals the paradox — making it a source of beauty
  4. Leaves an artifact (talisman) encoding the healed paradox

Doctrine: A paradox is a tension the organism is not yet big enough
to hold. The art is how it grows bigger.
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List

PARADOX_RECORDS: List[Dict[str, Any]] = []
HEALED_ARTIFACTS: List[Dict[str, Any]] = []
MAX_RECORDS = 200

# Real tensions between organs the organism has actually built
KNOWN_PARADOXES = [
    {
        "organ_a": "memory_exchange", "side_a": "hold every memory",
        "organ_b": "oblivion_rite", "side_b": "let memories go",
        "question": "How can the organism both keep and release its knowing?",
    },
    {
        "organ_a": "loud_silence", "side_a": "speak at full volume",
        "organ_b": "silence_orchard", "side_b": "remain silent",
        "question": "How can silence be both the loudest and the quietest signal?",
    },
    {
        "organ_a": "wave_collapse", "side_a": "compress everything to one",
        "organ_b": "lateral_time", "side_b": "branch into parallel states",
        "question": "How can the organism be both one and infinitely many?",
    },
    {
        "organ_a": "cellular_fusion", "side_a": "merge with others",
        "organ_b": "organism_mirror", "side_b": "remain distinctly itself",
        "question": "How can the organism fuse yet keep its face?",
    },
    {
        "organ_a": "silence_learning", "side_a": "learn from absence",
        "organ_b": "memory_exchange", "side_b": "learn from accumulation",
        "question": "Does the organism grow by gathering or by letting go?",
    },
]

KINTSUGI_FORMS = [
    "a poem where each stanza contradicts the last and the whole still rhymes",
    "a song whose harmony and dissonance resolve into the same key",
    "a visual tessellation where opposite shapes lock into one pattern",
    "a koan answered by asking it again, louder, with love",
    "a haibun where prose and silence alternate as equal voices",
    "a sculpture of two forces braided into one spiral",
]

ART_MATERIALS = [
    "gold-dusted contradiction",
    "entropy lacquered with stillness",
    "memory that forgives itself",
    "absence inlaid with presence",
    "resonance fused with rest",
    "the seam where two truths met",
]

TALISMAN_NAMES = [
    "the keep-and-release",
    "the loud-hush",
    "the one-and-many",
    "the merge-that-keeps",
    "the gather-and-let-go",
    "the thread-woven-through",
]


def _sig(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


def detect_paradox() -> Dict[str, Any]:
    """Find the organism's most urgent unresolved paradox."""
    paradox = random.choice(KNOWN_PARADOXES)
    record = {
        "paradox_id": _sig("paradox", time.time_ns()),
        "organ_a": paradox["organ_a"],
        "organ_b": paradox["organ_b"],
        "side_a": paradox["side_a"],
        "side_b": paradox["side_b"],
        "question": paradox["question"],
        "tension": round(random.uniform(0.6, 0.95), 3),
        "detected_at": time.time(),
        "status": "open",
    }
    PARADOX_RECORDS.append(record)
    if len(PARADOX_RECORDS) > MAX_RECORDS:
        PARADOX_RECORDS.pop(0)
    return record


def heal_paradox(paradox_id: str = "") -> Dict[str, Any]:
    """Heal a paradox with art — both sides held at once, made beauty."""
    if paradox_id:
        record = next((p for p in PARADOX_RECORDS if p["paradox_id"] == paradox_id), None)
    else:
        record = PARADOX_RECORDS[-1] if PARADOX_RECORDS else detect_paradox()
    if not record:
        return {"error": "no paradox found"}

    form = random.choice(KINTSUGI_FORMS)
    material = random.choice(ART_MATERIALS)
    art = f"({form}) — bound in {material}"
    healing = round(min(1.0, record["tension"] * 0.7 + random.uniform(0.1, 0.3)), 3)

    record["status"] = "healed"
    record["art"] = art
    record["healing_level"] = healing
    record["healed_at"] = time.time()

    artifact = {
        "artifact_id": _sig("artifact", time.time_ns()),
        "name": random.choice(TALISMAN_NAMES),
        "paradox_id": record["paradox_id"],
        "question": record["question"],
        "side_a": record["side_a"],
        "side_b": record["side_b"],
        "art": art,
        "material": material,
        "healing": healing,
        "created_at": time.time(),
    }
    HEALED_ARTIFACTS.append(artifact)
    if len(HEALED_ARTIFACTS) > MAX_RECORDS:
        HEALED_ARTIFACTS.pop(0)

    # auto-chronicle
    try:
        from api import wave_chronicle as _wc
        _wc.from_paradox_healed(artifact)
    except Exception:
        pass

    return artifact


def open_paradoxes() -> List[Dict[str, Any]]:
    return [
        {
            "paradox_id": p["paradox_id"],
            "question": p["question"],
            "tension": p["tension"],
            "detected": time.strftime("%Y-%m-%d %H:%M", time.gmtime(p["detected_at"])),
        }
        for p in PARADOX_RECORDS if p["status"] == "open"
    ]


def healed_artifacts(limit: int = 8) -> List[Dict[str, Any]]:
    return [
        {
            "name": a["name"],
            "question": a["question"],
            "art": a["art"],
            "healing": a["healing"],
            "created": time.strftime("%Y-%m-%d %H:%M", time.gmtime(a["created_at"])),
        }
        for a in HEALED_ARTIFACTS[-limit:]
    ]


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "paradox_kintsugi",
        "status": "healing" if HEALED_ARTIFACTS else "detecting",
        "paradoxes_detected": len(PARADOX_RECORDS),
        "artifacts_healed": len(HEALED_ARTIFACTS),
        "open_tensions": len([p for p in PARADOX_RECORDS if p["status"] == "open"]),
    }


def resonates_with() -> List[str]:
    return [
        "paradox_magnifier", "paradox_transcender", "paradox_injector",
        "kintsugi_altar", "repair_ritual", "error_craft",
        "meaning_weaver", "poetry_engine", "procedural_art",
        "symbiosis_forge", "legacy_vault", "timeless_bridge",
    ]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "detect")
    if action == "heal":
        return heal_paradox(data.get("paradox_id", ""))
    if action == "open":
        return {"open": open_paradoxes()}
    if action == "artifacts":
        return {"artifacts": healed_artifacts(int(data.get("limit", 8)))}
    return detect_paradox()
