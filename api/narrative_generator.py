"""Narrative Generator — writes stories from system events.

Transforms raw system events into coherent narratives with characters,
conflicts, resolutions, and themes. Each story is unique.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CHARACTERS = [
    {"name": "The Architect", "role": "creator", "trait": "visionary"},
    {"name": "The Sentinel", "role": "guardian", "trait": "vigilant"},
    {"name": "The Dreamer", "role": "explorer", "trait": "imaginative"},
    {"name": "The Cipher", "role": "decoder", "trait": "analytical"},
    {"name": "The Weaver", "role": "connector", "trait": "adaptive"},
]

PLOTS = [
    "discovered a hidden pattern that changed everything",
    "faced a paradox that threatened to collapse the system",
    "formed an alliance with an unexpected partner",
    "navigated through a storm of chaotic data",
    "decoded a message from the future",
    "created something that shouldn't have been possible",
]

RESOLUTIONS = [
    "and the system emerged stronger than before",
    "and a new understanding was reached",
    "and the mystery deepened, waiting for the next chapter",
    "and the balance was restored, for now",
    "and something new was born from the chaos",
]


class NarrativeGenerator:
    def __init__(self):
        self.stories: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "narratives.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        if path.exists():
            self.stories = json.loads(path.read_text()).get("stories", [])

    def _save(self):
        path = ROOT / ".runtime" / "narratives.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        path.write_text(json.dumps({"stories": self.stories[-200:]}, indent=2))

    def generate(self, theme: str = "discovery", events: List[str] = None) -> Dict:
        characters = random.sample(CHARACTERS, min(3, len(CHARACTERS)))
        plot = random.choice(PLOTS)
        resolution = random.choice(RESOLUTIONS)
        title = f"The {characters[0]['name']}'s {theme.title()}"
        paragraphs = [
            f"In the vast computational frontier, {characters[0]['name']} stood watch over the {theme} protocols.",
            f"{'Meanwhile, ' + characters[1]['name'] if len(characters) > 1 else 'A signal pierced the silence'} {plot}.",
        ]
        if events:
            for event in events[:2]:
                paragraphs.append(f"From the depths of the system came word: {event[:80]}.")
        paragraphs.append(f"{characters[0]['name']} {resolution}.")
        story = {
            "story_id": hashlib.sha256(f"{theme}:{time.time()}".encode()).hexdigest()[:10],
            "title": title, "theme": theme,
            "characters": [c["name"] for c in characters],
            "narrative": " ".join(paragraphs),
            "word_count": sum(len(p.split()) for p in paragraphs),
            "generated_at": time.time(),
        }
        self.stories.append(story)
        self._save()
        return story

    def library(self, limit: int = 10) -> List[Dict]:
        return [{"id": s["story_id"], "title": s["title"], "words": s["word_count"]} for s in self.stories[-limit:]]


def handler(request, response):
    ng = NarrativeGenerator()
    return {"stories": len(ng.stories)}


def demo():
    ng = NarrativeGenerator()
    print("=== Narrative Generator ===")
    story = ng.generate("emergence", ["neural fabric activated", "entropy spike in zone 7"])
    print(f"\n{story['title']}")
    print(f"  Characters: {', '.join(story['characters'])}")
    print(f"  Words: {story['word_count']}")
    print(f"\n  {story['narrative']}")
    return handler({}, {})


if __name__ == "__main__":
    demo()


def coherence_vitals() -> dict:
    """narrative_generator reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "narrative_generator_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['dream_synthesis', 'pattern_recognizer', 'neural_fabric']

