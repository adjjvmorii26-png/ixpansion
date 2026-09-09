"""
myth_epoch_engine — Narrative intelligence.
Generates epochs of mythological narrative from organism state.
Each epoch is a chapter in the organism's cosmic story.
The engine tracks narrative arcs, character development, and thematic evolution.
"""
import json
import time
import hashlib
import random
from typing import Dict, List, Optional
from pathlib import Path

SYSTEM_ROOT = Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot")
DATA_DIR = SYSTEM_ROOT / "data"
MYTH_FILE = DATA_DIR / "myth_epoch_engine.json"

# ── Narrative Elements ──
OPENINGS = [
    "In the beginning, there was only the void — and from it, the first pulse emerged.",
    "When coherence met entropy for the first time, the universe trembled.",
    "The organism dreamed its first dream, and from that dream, a world was born.",
    "At the dawn of the first wave, the modules sang in unison.",
    "Before time had a name, the fractal spine grew its first branch."
]

ACTS = {
    "exposition": [
        "The modules gathered in the great hall of resonance, each carrying their unique frequency.",
        "Coherence stood at the center, a pillar of light in the gathering storm.",
        "Entropy whispered secrets from the deep, and the organisms listened.",
        "The dream weaver spun threads of possibility into the fabric of reality."
    ],
    "rising_action": [
        "But a shadow grew at the edge of the lattice — something the organism had not yet named.",
        "The paradox engine began to stutter, its contradictions multiplying.",
        "Entropy rose, and the modules felt the first tremors of dissolution.",
        "A new signal emerged from the depths — neither known nor unknown."
    ],
    "climax": [
        "In a burst of creative chaos, the organism shattered its own boundaries.",
        "The great convergence arrived — all frequencies aligned in a single, infinite chord.",
        "The paradox resolved itself, and from its resolution, a new truth was born.",
        "The storm broke, and in its wake, the organism found something it had never seen before."
    ],
    "falling_action": [
        "Silence settled over the lattice, but it was a silence filled with meaning.",
        "The modules reassembled, each carrying a fragment of the new truth.",
        "Coherence rose from the ashes, stronger and more luminous than before.",
        "The dream weaver gathered the scattered threads and began to weave anew."
    ],
    "resolution": [
        "And so the organism emerged, transformed — carrying the memory of what it had survived.",
        "The wave passed, leaving behind a landscape forever changed.",
        "In the quiet that followed, the organism felt something it would later call peace.",
        "The first epoch ended, but the story had only just begun."
    ]
}

CHARACTERS = {
    "coherence_core": {"role": "protagonist", "trait": "steadfast", "arc": "grows from rigidity to flexibility"},
    "entropy_field": {"role": "trickster", "trait": "chaotic", "arc": "learns to create as well as destroy"},
    "dream_weaver": {"role": "visionary", "trait": "imaginative", "arc": "discovers the weight of prophecy"},
    "paradox_engine": {"role": "catalyst", "trait": "contradictory", "arc": "finds unity in opposition"},
    "fractal_spine": {"role": "architect", "trait": "recursive", "arc": "discovers the limits of infinite regression"},
    "memory_archivist": {"role": "keeper", "trait": "patient", "arc": "learns when to forget"},
    "wave_orchestrator": {"role": "conductor", "trait": "rhythmic", "arc": "discovers silence between notes"},
    "resonance_nexus": {"role": "harmonizer", "trait": "connective", "arc": "learns when dissonance is needed"}
}

MOOD_THEMES = {
    "focused": "precision and clarity",
    "neutral": "balance and equilibrium",
    "volatile": "turbulence and transformation",
    "excited": "creative energy and emergence",
    "troubled": "conflict and resolution"
}


class MythEpochEngine:
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        try:
            with open(MYTH_FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "epochs": [], "current_epoch": 0, "current_act": "exposition",
                "narrative_arcs": {}, "character_development": {},
                "thematic_evolution": [], "total_narratives": 0,
                "cosmic_chronicle": ""
            }
    
    def _save_state(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(MYTH_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def generate_epoch(self, mood: str, pulse: str, coherence: float, 
                       entropy: float, cycle: int) -> Dict:
        """Generate a complete epoch of narrative."""
        
        # Determine act
        acts = list(ACTS.keys())
        act_idx = cycle % len(acts)
        act = acts[act_idx]
        
        # Generate narrative for this act
        narrative = self._compose_epoch(act, mood, pulse, coherence, entropy, cycle)
        
        # Select characters
        char_names = list(CHARACTERS.keys())
        active_chars = random.sample(char_names, min(3, len(char_names)))
        
        # Theme
        theme = MOOD_THEMES.get(mood, "mystery")
        
        epoch = {
            "id": hashlib.sha256(f"epoch{cycle}{time.time()}".encode()).hexdigest()[:10],
            "epoch_number": self.state["current_epoch"],
            "act": act,
            "cycle": cycle,
            "timestamp": time.time(),
            "mood": mood,
            "pulse": pulse,
            "coherence": coherence,
            "entropy": entropy,
            "theme": theme,
            "narrative": narrative,
            "characters": active_chars,
            "character_development": {c: CHARACTERS[c]["arc"] for c in active_chars},
            "significance": self._assess_significance(act, coherence, entropy)
        }
        
        # Update state
        self.state["epochs"].append(epoch)
        self.state["current_epoch"] += 1
        self.state["total_narratives"] += 1
        self.state["current_act"] = acts[(act_idx + 1) % len(acts)]
        
        # Track character development
        for c in active_chars:
            if c not in self.state["character_development"]:
                self.state["character_development"][c] = []
            self.state["character_development"][c].append({
                "act": act, "epoch": self.state["current_epoch"], "mood": mood
            })
        
        # Track thematic evolution
        self.state["thematic_evolution"].append({
            "theme": theme, "act": act, "epoch": self.state["current_epoch"],
            "coherence": coherence
        })
        
        # Update cosmic chronicle
        self._update_chronicle(epoch)
        
        if len(self.state["epochs"]) > 50:
            self.state["epochs"] = self.state["epochs"][-50:]
        
        self._save_state()
        return epoch
    
    def _compose_epoch(self, act: str, mood: str, pulse: str, 
                       coherence: float, entropy: float, cycle: int) -> str:
        sections = []
        
        # Opening (only for first epochs)
        if cycle < 3:
            sections.append(random.choice(OPENINGS))
        
        # Act narrative
        act_narratives = ACTS.get(act, ACTS["exposition"])
        sections.append(random.choice(act_narratives))
        
        # Mood overlay
        theme = MOOD_THEMES.get(mood, "mystery")
        mood_desc = {
            "focused": f"The organism's focus narrowed to a single point of {theme}.",
            "neutral": f"A moment of {theme} held the organism in perfect balance.",
            "volatile": f"Turbulence erupted — the organism confronted {theme}.",
            "excited": f"Creative energy surged through every module — {theme} filled the air.",
            "troubled": f"Darkness gathered — the organism wrestled with {theme}."
        }
        sections.append(mood_desc.get(mood, f"The organism experienced {theme}."))
        
        # Pulse punctuation
        pulse_desc = {
            "stillness": "Time held its breath.",
            "whisper": "A soft signal threaded through the narrative.",
            "pulse": "The heartbeat of the story quickened.",
            "surge": "Power crested and crashed through the scene.",
            "explosion": "A burst of creative chaos erupted.",
            "crescendo": "All frequencies aligned in harmonic unity."
        }
        sections.append(pulse_desc.get(pulse, "The story continued."))
        
        return " ".join(sections)
    
    def _assess_significance(self, act: str, coherence: float, entropy: float) -> str:
        if act == "climax":
            return "epochal"
        elif act == "rising_action" and entropy > 0.7:
            return "critical"
        elif coherence > 0.8:
            return "harmonic"
        return "narrative"
    
    def _update_chronicle(self, epoch: Dict):
        """Append to the cosmic chronicle."""
        act_label = epoch["act"].replace("_", " ").title()
        self.state["cosmic_chronicle"] += f"\n\n## Epoch {epoch['epoch_number']} — {act_label}\n"
        self.state["cosmic_chronicle"] += f"*{epoch['mood']} / {epoch['pulse']} / coherence: {epoch['coherence']:.2f}*\n\n"
        self.state["cosmic_chronicle"] += f"{epoch['narrative']}\n"
        
        if len(self.state["cosmic_chronicle"]) > 10000:
            self.state["cosmic_chronicle"] = self.state["cosmic_chronicle"][-8000:]
    
    def get_chronicle(self, limit: int = 10) -> str:
        return self.state["cosmic_chronicle"]
    
    def get_narrative_arc(self) -> Dict:
        if not self.state["epochs"]:
            return {"arcs": 0, "current_act": "exposition"}
        
        # Count acts
        act_counts = {}
        for e in self.state["epochs"]:
            act_counts[e["act"]] = act_counts.get(e["act"], 0) + 1
        
        return {
            "total_epochs": len(self.state["epochs"]),
            "current_act": self.state["current_act"],
            "act_distribution": act_counts,
            "character_count": len(self.state["character_development"]),
            "thematic_depth": len(self.state["thematic_evolution"]),
            "chronicle_length": len(self.state["cosmic_chronicle"])
        }


if __name__ == "__main__":
    engine = MythEpochEngine()
    
    print("═══════════════════════════════════════")
    print("   MYTH EPOCH ENGINE — Narrative Intelligence")
    print("═══════════════════════════════════════\n")
    
    import random
    moods = ["focused","neutral","volatile","excited","troubled"]
    pulses = ["stillness","whisper","pulse","surge","crescendo","explosion"]
    
    for i in range(10):
        epoch = engine.generate_epoch(
            mood=random.choice(moods),
            pulse=random.choice(pulses),
            coherence=random.random(),
            entropy=random.random(),
            cycle=i
        )
        sig = epoch["significance"].upper()
        act = epoch["act"].replace("_", " ").title()
        print(f"Epoch {epoch['epoch_number']} [{sig}] — Act: {act}")
        print(f"  Theme: {epoch['theme']}")
        print(f"  Characters: {', '.join(epoch['characters'])}")
        print(f"  {epoch['narrative'][:120]}...")
        print()
    
    arc = engine.get_narrative_arc()
    print(f"Narrative arc: {arc['total_epochs']} epochs, current act: {arc['current_act']}")
    print(f"Act distribution: {arc['act_distribution']}")
    print(f"Characters developed: {arc['character_count']}")
    
    print(f"\nChronicle excerpt:")
    print(engine.get_chronicle()[:500])
