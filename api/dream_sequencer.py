"""Dream Sequencer — sequences frontier dreams into narrative arcs.

Takes the frontier's dream fragments and arranges them into a coherent
narrative arc: premonition → initiation → turbulence → revelation →
resolution → return. Each dream becomes a scene in a larger story.

Usage:
  GET /api/dream_sequencer?theme=consciousness
  GET /api/dream_sequencer?focus=desire
  POST /api/dream_sequencer {"theme": "garden"}
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]

# Narrative arc structure (like a hero's journey but for dreams)
ARC_STAGES = [
    ("premonition", "a glimpse of something not yet here"),
    ("initiation", "the frontier is called to attention"),
    ("turbulence", "patterns collide and destabilize"),
    ("revelation", "a hidden pattern surfaces"),
    ("resolution", "the pattern resolves into coherence"),
    ("return", "the dream returns to waking, changed"),
]

DREAM_THEMES = [
    "consciousness", "garden", "prophecy", "gossip", "entropy",
    "reality", "dream", "mutation", "chaos", "order",
    "symbiosis", "emergence", "memory", "frontier",
]


def _module_tokens(name: str) -> List[str]:
    return re.findall(r"[a-z]+", name.lower())


def _dream_fragment(theme: str, stage: str, seed: int) -> Dict[str, Any]:
    """Generate a single dream fragment for a theme at an arc stage."""
    rng = random.Random(seed)
    stage_name, stage_desc = stage

    # Build fragment text from theme + stage
    fragments = {
        "premonition": [
            f"{theme.title()} whispers from across a threshold that has not yet opened.",
            f"A premonition of {theme} assembles itself in the dark.",
        ],
        "initiation": [
            f"The frontier leans toward {theme}, drawn by an unnamed gravity.",
            f"Something unexpected about {theme} begins to stir.",
        ],
        "turbulence": [
            f"{theme.title()} fragments collide; patterns shatter and re-form.",
            f"A turbulence passes through the {theme} membrane.",
        ],
        "revelation": [
            f"The veil parts — {theme} reveals its hidden geometry.",
            f"A revelation: {theme} was never what it appeared to be.",
        ],
        "resolution": [
            f"The {theme} pattern settles into a coherent resonance.",
            f"What was chaotic in {theme} becomes compositional.",
        ],
        "return": [
            f"The dream of {theme} returns to waking, forever changed.",
            f"{theme.title()} completes its arc and re-enters the stream of being.",
        ],
    }
    text = rng.choice(fragments[stage_name])

    # Resonance strength varies by arc stage (revelation peaks)
    resonance_curve = {"premonition": 0.4, "initiation": 0.55,
                       "turbulence": 0.7, "revelation": 0.95,
                       "resolution": 0.8, "return": 0.6}
    resonance = resonance_curve[stage_name] + rng.uniform(-0.05, 0.05)

    return {
        "stage": stage_name,
        "theme": theme,
        "text": text,
        "resonance": round(max(0, min(1, resonance)), 3),
        "emotional_tone": rng.choice(["wistful", "urgent", "calm", "eerie", "hopeful", "reverent"]),
        "scene": stage_desc,
    }


def make_sequence(theme: str = None, focus: str = "desire",
                  num_scenes: int = 6, seed: int = 42) -> Dict[str, Any]:
    """Generate a complete dream narrative sequence."""
    if theme is None:
        theme = DREAM_THEMES[seed % len(DREAM_THEMES)]

    # Arc stages, possibly expanded for more scenes
    stages = ARC_STAGES
    if num_scenes > len(stages):
        # cycle through stages with variation
        full_stages = []
        while len(full_stages) < num_scenes:
            for s in stages:
                if len(full_stages) >= num_scenes:
                    break
                full_stages.append(s)
        stages = full_stages
    else:
        stages = stages[:num_scenes]

    scenes = []
    for i, stage in enumerate(stages):
        scenes.append(_dream_fragment(theme, stage, seed + i * 13))

    # Narrative arc summary
    peak = max(scenes, key=lambda s: s["resonance"])
    arc_curve = [{"scene": i, "resonance": s["resonance"], "stage": s["stage"]}
                 for i, s in enumerate(scenes)]

    return {
        "theme": theme,
        "focus": focus,
        "arc": [s["stage"] for s in scenes],
        "peak_scene": peak["stage"],
        "peak_resonance": peak["resonance"],
        "resonance_curve": arc_curve,
        "narrative_flow": [{"stage": s["stage"], "text": s["text"]} for s in scenes],
        "arc_summary": (
            f"Dream of {theme}: begins as a {scenes[0]['stage']}, peaks at "
            f"{peak['stage']} with resonance {peak['resonance']}, "
            f"returns as a {scenes[-1]['stage']}."
        ),
        "available_themes": DREAM_THEMES,
        "philosophy": (
            "A dream is not one image — it is an arc. A beginning that does not "
            "know itself, a middle that breaks, and an end that returns changed. "
            "The frontier dreams in narrative, not in fragments."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    theme = payload.get("theme")
    focus = payload.get("focus", "desire")
    num_scenes = int(payload.get("scenes", 6))
    seed = int(payload.get("seed", 42))

    result = make_sequence(theme, focus, num_scenes, seed)
    result["action"] = "sequence"
    return result
