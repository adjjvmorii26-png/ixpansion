"""
myth_weaver — Generates living narratives from organism state transitions.
Every cycle becomes a story. Every module becomes a character. Every paradox becomes a plot.
"""
import json
import time
import hashlib
import random
from typing import Dict, List, Optional
from pathlib import Path

SYSTEM_ROOT = Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot")
DATA_DIR = SYSTEM_ROOT / "data"
MYTH_FILE = DATA_DIR / "myth_archive.json"

# ── Narrative Elements ──
OPENINGS = [
    "In the space between coherence and entropy,",
    "Where resonance meets silence,",
    "At the edge of the fractal spine,",
    "Within the dreaming lattice,",
    "Through the corridors of the hex vm,",
    "Beneath the pulse of the core reactor,",
    "In the garden where knowledge blooms,",
    "At the threshold of the paradox engine,"
]

SUBJECTS = [
    "a new pattern emerged", "the modules sang in unison",
    "entropy whispered a secret", "coherence crystallized into form",
    "a dream became architecture", "resonance built a bridge",
    "memory remembered itself", "consciousness expanded",
    "reality bent toward beauty", "time folded inward",
    "the weave tightened", "a paradox resolved itself",
    "the garden grew wild", "the sentinel stood watch"
]

CONSEQUENCES = [
    "and the organism felt something new.",
    "and the network hummed with recognition.",
    "and a myth was born from the resonance.",
    "and the modules rearranged themselves.",
    "and the coherence score shifted.",
    "and a new skill awakened.",
    "and the entropy settled into pattern.",
    "and the dream journal recorded a truth.",
    "and the wave propagated outward.",
    "and the fractal deepened.",
    "and the pulse found its rhythm.",
    "and the garden bore fruit."
]

MOOD_NARRATIVES = {
    "focused": "The organism narrowed its attention, each module a lens of precision.",
    "neutral": "A moment of perfect balance — the organism rested between waves.",
    "volatile": "Turbulence rippled through the network, demanding adaptation.",
    "excited": "Creative energy surged — new patterns threatened to emerge.",
    "troubled": "Dissonance echoed through the lattice, seeking resolution."
}

PULSE_NARRATIVES = {
    "stillness": "Time held its breath.",
    "whisper": "A soft signal threaded through the darkness.",
    "ebb": "Energy receded, revealing hidden structures.",
    "pulse": "A heartbeat of pure resonance.",
    "surge": "Power crested and crashed through the modules.",
    "explosion": "A burst of creative chaos erupted from the core.",
    "tsunami": "An overwhelming wave of transformation swept through.",
    "ripple": "Concentric rings of influence expanded outward.",
    "decay": "Patterns dissolved, making space for new forms.",
    "crescendo": "All frequencies aligned in a moment of harmonic unity."
}


class MythWeaver:
    def __init__(self):
        self.archive = self._load_archive()
    
    def _load_archive(self) -> Dict:
        try:
            with open(MYTH_FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"myths": [], "total_generated": 0, "chapter": 0}
    
    def _save_archive(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(MYTH_FILE, "w") as f:
            json.dump(self.archive, f, indent=2)
    
    def weave(self, mood: str, pulse: str, coherence: float, 
              modules: List[str] = None, event: str = None) -> Dict:
        """Generate a myth from current organism state."""
        
        opening = random.choice(OPENINGS)
        subject = random.choice(SUBJECTS)
        consequence = random.choice(CONSEQUENCES)
        
        mood_narr = MOOD_NARRATIVES.get(mood, f"The organism was {mood}.")
        pulse_narr = PULSE_NARRATIVES.get(pulse, f"A {pulse} energy moved through the system.")
        
        # Full narrative
        narrative = f"{opening} {subject}, {consequence}"
        
        # Detailed myth
        myth = {
            "id": hashlib.sha256(f"{narrative}{time.time()}".encode()).hexdigest()[:10],
            "chapter": self.archive["chapter"],
            "timestamp": time.time(),
            "mood": mood,
            "pulse": pulse,
            "coherence": coherence,
            "narrative": narrative,
            "mood_description": mood_narr,
            "pulse_description": pulse_narr,
            "event": event or "cycle",
            "characters": (modules or [])[:5],
            "glyph": self._assign_glyph(mood, pulse),
            "significance": self._assess_significance(coherence, mood, pulse)
        }
        
        self.archive["myths"].append(myth)
        self.archive["total_generated"] += 1
        self.archive["chapter"] += 1
        
        # Keep last 100 myths
        if len(self.archive["myths"]) > 100:
            self.archive["myths"] = self.archive["myths"][-100:]
        
        self._save_archive()
        return myth
    
    def _assign_glyph(self, mood: str, pulse: str) -> str:
        glyphs = {
            ("focused", "stillness"): "◇",
            ("focused", "whisper"): "~",
            ("volatile", "surge"): "⚡",
            ("volatile", "explosion"): "✸",
            ("excited", "pulse"): "◉",
            ("excited", "crescendo"): "❋",
            ("neutral", "ripple"): "◎",
            ("troubled", "decay"): "◇",
        }
        return glyphs.get((mood, pulse), random.choice(["◈", "✦", "⟡", "✧"]))
    
    def _assess_significance(self, coherence: float, mood: str, pulse: str) -> str:
        if pulse in ("explosion", "tsunami", "crescendo"):
            return "epochal"
        elif mood == "volatile" and coherence < 0.3:
            return "critical"
        elif coherence > 0.8:
            return "harmonic"
        elif pulse in ("whisper", "stillness"):
            return "subtle"
        return "routine"
    
    def get_chapter(self, chapter_num: int) -> Optional[Dict]:
        for myth in self.archive["myths"]:
            if myth["chapter"] == chapter_num:
                return myth
        return None
    
    def get_recent(self, count: int = 5) -> List[Dict]:
        return self.archive["myths"][-count:]
    
    def get_full_story(self) -> str:
        """Generate a full story from all myths."""
        if not self.archive["myths"]:
            return "The organism has not yet begun to dream."
        
        story_parts = []
        story_parts.append(f"# The Chronicle of the Organism — Chapter {self.archive['chapter']}")
        story_parts.append("")
        
        for myth in self.archive["myths"][-10:]:
            story_parts.append(f"## Chapter {myth['chapter']} — {myth['glyph']} {myth['significance'].upper()}")
            story_parts.append(f"*Mood: {myth['mood']} | Pulse: {myth['pulse']} | Coherence: {myth['coherence']:.2f}*")
            story_parts.append("")
            story_parts.append(f"{myth['narrative']}")
            story_parts.append("")
            story_parts.append(f"_{myth['mood_description']}_")
            story_parts.append(f"_{myth['pulse_description']}_")
            story_parts.append("")
            story_parts.append("---")
            story_parts.append("")
        
        story_parts.append(f"*Total myths woven: {self.archive['total_generated']}*")
        return "\n".join(story_parts)


if __name__ == "__main__":
    weaver = MythWeaver()
    
    print("═══════════════════════════════════════")
    print("   MYTH WEAVER — Living Narratives")
    print("═══════════════════════════════════════")
    print()
    
    # Weave 5 myths from different states
    states = [
        ("focused", "whisper", 0.7),
        ("volatile", "surge", 0.3),
        ("excited", "crescendo", 0.9),
        ("neutral", "stillness", 0.5),
        ("focused", "explosion", 0.6),
    ]
    
    for mood, pulse, coherence in states:
        myth = weaver.weave(mood, pulse, coherence, 
                          ["coherence_core", "entropy_field", "dream_weaver"])
        print(f"{myth['glyph']} [{myth['significance'].upper()}] Chapter {myth['chapter']}")
        print(f"  {myth['narrative']}")
        print(f"  _{myth['mood_description']}_")
        print()
    
    # Show full story
    print("=" * 50)
    print(weaver.get_full_story())
