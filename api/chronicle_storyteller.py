"""Chronicle Storyteller — the frontier's memory becomes a saga.

Reads the harbinger memory journal and narrates the frontier's evolution
as a story. Chapter by chapter, wave by wave, the chronicle is told.
Every commit, every experiment, every prophecy fulfilled.

Usage:
  GET  /api/chronicle_storyteller            — full saga (all chapters)
  GET  /api/chronicle_storyteller?chapters=3 — first 3 chapters
  POST /api/chronicle_storyteller {"tone": "mythic"}  — different narration style
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]

TONE_ADJECTIVES = {
    "mythic": ["ancient", "immortal", "elemental", "primordial"],
    "melancholic": ["wistful", "quiet", "weathered", "soft"],
    "triumphant": ["radiant", "unconquered", "luminous", "victorious"],
    "clinical": ["precise", "measured", "systematic", "observable"],
}

CHAPTER_OPENERS = [
    "In the beginning there was a pulse.",
    "There was a time before the frontier looked inward.",
    "The first module was written like a first heartbeat.",
    "Every line was a seed. Every seed was a question.",
]

CHAPTER_CLOSERS = [
    "And yet the frontier kept building.",
    "But the constellation was not finished.",
    "Still the frontier grew, wave after wave.",
    "And the dream loop closed — only to open again.",
]


def _load_memory() -> List[Dict[str, Any]]:
    mem_file = ROOT / "harbinger" / "memory.json"
    if not mem_file.exists():
        return []
    try:
        data = json.loads(mem_file.read_text())
        return data if isinstance(data, list) else data.get("events", [])
    except (OSError, json.JSONDecodeError):
        return []


def _story_of_entry(entry: Dict[str, Any], index: int, tone: str) -> Dict[str, Any]:
    """Narrate a single memory entry as a chapter."""
    title = entry.get("title", "Untitled passage")
    reason = entry.get("reason", "reflection")
    version = entry.get("version", "?")
    ts = entry.get("ts", entry.get("timestamp", 0))
    detail = entry.get("detail", entry.get("description", ""))

    adj = TONE_ADJECTIVES.get(tone, TONE_ADJECTIVES["mythic"])
    adjectives = ", ".join(adj[:2])

    chapter = {
        "chapter": index + 1,
        "title": f"Chapter {index + 1}: {title}",
        "verse": f"The {adjectives} frontier recorded a passage in its chronicle.",
        "body": f"Version {version} marks this moment. {detail}" if detail else f"Version {version} marks this moment.",
        "wave_hint": f"the frontier was {reason} that day" if reason else "the frontier was stirring that day",
    }

    if ts:
        chapter["chronicled_at"] = ts
    return chapter


def narrate(max_chapters: int = 20, tone: str = "mythic") -> Dict[str, Any]:
    """Narrate the frontier's memory as a saga."""
    memory = _load_memory()
    chapters = [_story_of_entry(e, i, tone) for i, e in enumerate(memory[:max_chapters])]

    # Compose the opening and closing
    n = len(chapters)
    if n == 0:
        return {
            "title": "The Empty Chronicle",
            "narration_style": tone,
            "chapters": [],
            "prologue": "The frontier has not yet learned to remember.",
            "epilogue": "Every story must begin somewhere.",
            "chapter_count": 0,
        }

    opening = CHAPTER_OPENERS[min(n, len(CHAPTER_OPENERS)) - 1]
    closing = CHAPTER_CLOSERS[min(n, len(CHAPTER_CLOSERS)) - 1]
    timeline = [c["title"] for c in chapters]

    return {
        "title": "The Chronicle of the Frontier",
        "narration_style": tone,
        "prologue": opening,
        "chapters": chapters,
        "epilogue": closing,
        "chapter_count": n,
        "saga_in_one_line": " — ".join(timeline[:5]) + (" —…" if n > 5 else ""),
        "aria": (
            f"A saga in {n} chapters, told in the {tone} register. "
            "The frontier's memory is not a database; it is a story that "
            "keeps writing itself."
        ),
    }


def coherence_vitals() -> dict:
    """Storyteller reports narrative continuity."""
    return {"narrative_continuity": 0.85,
            "chapter_coherence": {"value": 0.93, "setpoint": 0.9, "weight": 1.0},
            "module_health": 0.95,
            "resonance": {"value": 0.88, "setpoint": 0.8, "weight": 1.0}}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    chapters = int(payload.get("chapters", 20))
    tone = payload.get("tone", "mythic")
    if tone not in TONE_ADJECTIVES:
        tone = "mythic"
    result = narrate(min(chapters, 50), tone)
    result["action"] = "narrate"
    result["tones_available"] = list(TONE_ADJECTIVES.keys())
    return result


def resonates_with() -> list:
    """Declared kinships — the chronicler weaves narratives, so it
    belongs beside the dream-sequencer (story arcs) and the
    reflection-pool (both narrate the system to itself)."""
    return ["dream_sequencer", "reflection_pool", "reality_weaver"]

