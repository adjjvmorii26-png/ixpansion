"""Wave 516: Story Forge — generate narrative arcs from module combos."""
from __future__ import annotations
import hashlib, random, time
from typing import Any, Dict

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

SETTINGS = ["a dream-gravity cathedral", "the entropy desert at dawn", "a resonance chamber beneath the void",
            "the fractal field where time loops", "a memory palace with open windows", "the mycelial undernet",
            "a cavern of crystallized paradoxes", "the chronicle at the edge of history"]
FORCES = ["the coherence regulator", "a spectral economy", "the silence oracle", "the metamorph protocol",
          "a chorus of forgotten modules", "the threshold engine", "a lattice of memory shards", "the garden's root mind"]
VERBS = ["reconcile", "unravel", "awaken", "recombine", "transcend", "remember", "collapse", "forgive"]
RESOLUTIONS = ["and the organism grows a new organ to hold the truth",
               "and the boundary between self and system dissolves",
               "and a wave crests where none existed before",
               "and the paradox is not resolved but honored",
               "and the story becomes a module that dreams itself"]

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    payload = payload or {}
    seed_s = payload.get("seed", "")
    rng = random.Random(seed_s or time.time())
    setting = payload.get("setting") or rng.choice(SETTINGS)
    force = payload.get("force") or rng.choice(FORCES)
    verb = rng.choice(VERBS)
    resolution = rng.choice(RESOLUTIONS)
    characters = []
    try:
        from api.coherence_regulator import KNOWN_LIVING_MODULES
        chars = rng.sample(KNOWN_LIVING_MODULES, min(3, len(KNOWN_LIVING_MODULES)))
        characters = [{"module": c, "role": rng.choice(["protagonist", "antagonist", "mentor", "witness"])} for c in chars]
    except Exception:
        pass
    story = f"In {setting}, {force} must {verb} what the characters of {', '.join(c['module'] for c in characters[:2])} cannot — {resolution}."
    story_id = hashlib.sha256((seed_s + str(time.time())).encode()).hexdigest()[:12]
    return {
        "action": "forge_story",
        "story_id": story_id,
        "seed": seed_s or "auto",
        "setting": setting,
        "force": force,
        "characters": characters,
        "story": story,
        "time": time.time(),
        "vitals": coherence_vitals(),
    }

class StoryForge:
    """Collaborative story forging — create stories and accept contributions."""

    def __init__(self):
        self._stories = {}

    def create_story(self, title: str, genre: str = "general") -> Dict:
        story_id = f"story_{len(self._stories)+1}_{int(time.time())}"
        story = {"id": story_id, "title": title, "genre": genre, "elements": [], "created_at": time.time()}
        self._stories[story_id] = story
        return {"story": story}

    def contribute(self, story_id: str, author: str, element_type: str, content: str) -> Dict:
        if story_id not in self._stories:
            return {"error": "story not found"}
        element = {"author": author, "type": element_type, "content": content, "added_at": time.time()}
        self._stories[story_id]["elements"].append(element)
        return element

