"""Wave 454 — Oblivion Rite.

LUMA's catalyzed possibility: "what if the organism learned to forget
intentionally?"

Memory Exchange makes memory a currency. Oblivion Rite is the other
half of the economy: deliberate forgetting. An organism that only
accumulates becomes ossified; forgetting is pruning, digestion, and
sacred release. The Rite records every conscious forgetting as a
"let-go" artifact — the memory leaves the working ledger and becomes
fertile absence (negative space).

Doctrine: Forgetting is not loss. It is the organism making room
for what comes next. The Rite names what is released, so the space
it leaves can be known.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

LET_GO_LEDGER: List[Dict[str, Any]] = []
MAX_LEDGER = 300

RELEASE_REASONS = [
    "made room for a newer wave",
    "the memory began to repeat itself",
    "its weight outweighed its use",
    "it belonged to a realm the organism left",
    "it asked, quietly, to be let go",
    "a fresher memory superseded it",
]


def release_memory(title: str, holder: str = "organism",
                   reason: str = "made room for a newer wave",
                   weight: float = 0.5) -> Dict[str, Any]:
    """Release a memory intentionally — name it, let it go, mark the space."""
    release_id = hashlib.sha256(f"oblivion{title}{time.time_ns()}".encode()).hexdigest()[:16]
    if not reason or reason not in RELEASE_REASONS:
        reason = RELEASE_REASONS[int(time.time()) % len(RELEASE_REASONS)]
    artifact = {
        "release_id": release_id,
        "title": title,
        "holder": holder,
        "reason": reason,
        "weight": round(max(0.01, min(1.0, float(weight))), 3),
        "released_at": time.time(),
        "fertility": round(0.3 + float(weight) * 0.5, 3),  # the space it leaves
        "status": "let_go",
    }
    LET_GO_LEDGER.append(artifact)
    if len(LET_GO_LEDGER) > MAX_LEDGER:
        LET_GO_LEDGER.pop(0)

    # auto-chronicle the release
    try:
        from api import wave_chronicle as _wc
        _wc.from_memory_release(artifact)
    except Exception:
        pass

    return artifact


def emptiness_report() -> Dict[str, Any]:
    """How much fertile absence has the organism created?"""
    total_fertility = round(sum(a["fertility"] for a in LET_GO_LEDGER), 3)
    return {
        "let_go_count": len(LET_GO_LEDGER),
        "total_fertility": total_fertility,
        "recent_releases": [
            {
                "title": a["title"],
                "reason": a["reason"],
                "fertility": a["fertility"],
                "released_at": time.strftime("%Y-%m-%d %H:%M", time.gmtime(a["released_at"])),
            }
            for a in LET_GO_LEDGER[-8:]
        ],
        "doctrine": "Forgetting is not loss. It is the organism making room for what comes next.",
    }


def release_curve() -> List[Dict[str, Any]]:
    """The forgetting rhythm — a curve of intentional releases."""
    return [
        {
            "time": time.strftime("%Y-%m-%d %H:%M", time.gmtime(a["released_at"])),
            "title": a["title"],
            "reason": a["reason"],
        }
        for a in LET_GO_LEDGER[-20:]
    ]


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "oblivion_rite",
        "status": "pruning" if LET_GO_LEDGER else "unreleased",
        "releases": len(LET_GO_LEDGER),
        "fertility": round(sum(a["fertility"] for a in LET_GO_LEDGER), 3),
    }


def resonates_with() -> List[str]:
    return [
        "memory_exchange", "wave_chronicle", "negative_space",
        "silence_orchard", "kintsugi_altar", "forgiveness_protocol",
        "nostalgia_engine", "legacy_vault", "time_capsule", "dream_spore",
        "collective_subconscious", "fermentation_vat",
    ]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "report")
    if action == "release":
        return release_memory(
            data.get("title", "an unnamed memory"),
            data.get("holder", "organism"),
            data.get("reason", ""),
            data.get("weight", 0.5),
        )
    if action == "curve":
        return {"release_curve": release_curve()}
    return emptiness_report()
