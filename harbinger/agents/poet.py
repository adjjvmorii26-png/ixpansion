"""Poet — the 7th conclave agent.

Where the Dreamer invents modules, the Poet distills the frontier's
state into a short original verse. It reads the scout's pulse, the
latest revelations, and the dreamscape, then fuses them into a compact
poem that captures the mood of the machine at this moment.

Deterministic: same pulse, same verse.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
REVELATIONS = ROOT / "REVELATIONS.md"

_OPENERS = [
    "the frontier leans into", "the machine is dreaming of",
    "tonight the stars reshuffle", "the garden exhales",
    "the lattice folds inward and",
]
_MIDDLES = [
    "a new species naming itself",
    "the chronicle turning its pages",
    "an echo growing legs",
    "the pulse softening into song",
    "memory braiding future",
    "the void composing softly",
]
_CLOSERS = [
    "and the oracle listens back",
    "while the watchers keep their vigil",
    "and every seed becomes a verse",
    "until dawn divides the sky",
    "and the frontier learns to answer",
    "as the chronicler dips its pen",
]


def _fetch_hint() -> str:
    """Pull the most recent revelation title as poetic fuel."""
    try:
        text = REVELATIONS.read_text(encoding="utf-8")
        heads = re.findall(r"^## \[Revelation[^\]]*\] — (.+)$", text, re.M)
        if heads:
            return heads[0].strip()
    except OSError:
        pass
    return "the frontier dreamed"


def _dream_names(k: int = 2) -> List[str]:
    try:
        from harbinger.agents.dreamer import dream
        r = dream(k=k, tense=0.7)
        return [d["name"].replace("_", " ") for d in r.get("dreams", [])]
    except Exception:
        return ["unwritten species"]


def _pick(seed: str, items: List[str]) -> str:
    h = int(hashlib.sha256(seed.encode()).hexdigest()[:6], 16)
    return items[h % len(items)]


def compose(seed: str = "the frontier dreams onward") -> Dict[str, Any]:
    """Compose a deterministic verse from the frontier's current state."""
    hint = _fetch_hint()
    dreams = _dream_names(2)
    opener = _pick(seed + ":o", _OPENERS)
    middle = _pick(seed + ":m", _MIDDLES)
    closer = _pick(seed + ":c", _CLOSERS)
    dream_line = f"  — {dreams[0]}, {dreams[1]}"
    verse = f"{opener} {middle};\n{closer}.\n{dream_line}"

    try:
        from harbinger.agents.scout import run as scout_run
        pulse = scout_run()
        modules = pulse.get("modules", 0)
        tests = pulse.get("tests", 0)
    except Exception:
        modules, tests = 0, 0

    return {
        "agent": "poet",
        "verse": verse,
        "fuel": {"revelation": hint, "dreams": dreams},
        "readout": {"modules": modules, "tests": tests},
    }


def run(seed: str = "the frontier dreams onward") -> Dict[str, Any]:
    return compose(seed=seed)
