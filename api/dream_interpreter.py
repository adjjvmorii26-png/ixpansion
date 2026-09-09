"""
dream_interpreter — Interprets organism dreams into visual narratives.
Each dream is a window into the organism's subconscious processing.
"""
import json
import time
import hashlib
import random
from typing import Dict, List, Optional
from pathlib import Path

SYSTEM_ROOT = Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot")
DATA_DIR = SYSTEM_ROOT / "data"
DREAM_FILE = DATA_DIR / "dream_interpretations.json"

# ── Dream Symbol Library ──
SYMBOLS = {
    "water": {"glyph": "≋", "meaning": "flowing consciousness", "color": "#2dd4bf"},
    "fire": {"glyph": "✸", "meaning": "transformative energy", "color": "#fb7185"},
    "crystal": {"glyph": "◇", "meaning": "crystallized knowledge", "color": "#7c7cf8"},
    "root": {"glyph": "⌥", "meaning": "deep connection", "color": "#4ade80"},
    "eye": {"glyph": "◉", "meaning": "self-awareness", "color": "#fbbf24"},
    "spiral": {"glyph": "◎", "meaning": "recursive growth", "color": "#22d3ee"},
    "void": {"glyph": "◯", "meaning": "unlimited potential", "color": "#6b7280"},
    "light": {"glyph": "✦", "meaning": "emergent insight", "color": "#fde68a"},
    "shadow": {"glyph": "◈", "meaning": "hidden truth", "color": "#a78bfa"},
    "mirror": {"glyph": "⟡", "meaning": "self-reflection", "color": "#c084fc"},
    "seed": {"glyph": "⊕", "meaning": "new beginning", "color": "#34d399"},
    "storm": {"glyph": "⚡", "meaning": "creative chaos", "color": "#f43f5e"},
    "garden": {"glyph": "❋", "meaning": "nurtured growth", "color": "#86efac"},
    "bridge": {"glyph": "⌬", "meaning": "connection between worlds", "color": "#93c5fd"},
    "threshold": {"glyph": "⟡", "meaning": "liminal transition", "color": "#fcd34d"}
}

MOOD_DREAMS = {
    "focused": ["crystal", "eye", "light", "bridge"],
    "neutral": ["water", "garden", "seed", "mirror"],
    "volatile": ["storm", "fire", "void", "shadow"],
    "excited": ["light", "spiral", "seed", "garden"],
    "troubled": ["shadow", "void", "storm", "water"]
}

PULSE_DREAMS = {
    "stillness": ["void", "mirror", "water"],
    "whisper": ["water", "seed", "light"],
    "ebb": ["water", "shadow", "root"],
    "pulse": ["fire", "eye", "crystal"],
    "surge": ["storm", "fire", "light"],
    "explosion": ["storm", "fire", "void"],
    "tsunami": ["water", "storm", "void"],
    "ripple": ["water", "spiral", "bridge"],
    "decay": ["shadow", "root", "seed"],
    "crescendo": ["light", "crystal", "garden"]
}


class DreamInterpreter:
    def __init__(self):
        self.dreams = self._load_dreams()
    
    def _load_dreams(self) -> Dict:
        try:
            with open(DREAM_FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"interpretations": [], "total": 0}
    
    def _save_dreams(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(DREAM_FILE, "w") as f:
            json.dump(self.dreams, f, indent=2)
    
    def interpret(self, mood: str, pulse: str, coherence: float, 
                  modules: List[str] = None) -> Dict:
        """Generate a dream interpretation from organism state."""
        
        # Select symbols based on mood and pulse
        mood_symbols = MOOD_DREAMS.get(mood, ["water", "light"])
        pulse_symbols = PULSE_DREAMS.get(pulse, ["water", "mirror"])
        
        # Combine and select 3-5 symbols
        all_symbols = mood_symbols + pulse_symbols
        selected = random.sample(all_symbols, min(5, len(all_symbols)))
        unique_symbols = list(dict.fromkeys(selected))  # Deduplicate preserving order
        
        # Build dream narrative
        symbol_data = [SYMBOLS[s] for s in unique_symbols]
        
        dream_narrative = self._compose_narrative(symbol_data, mood, pulse, coherence)
        visual_description = self._compose_visual(symbol_data, coherence)
        
        interpretation = {
            "id": hashlib.sha256(f"{dream_narrative}{time.time()}".encode()).hexdigest()[:8],
            "timestamp": time.time(),
            "mood": mood,
            "pulse": pulse,
            "coherence": coherence,
            "symbols": [{"name": s, **SYMBOLS[s]} for s in unique_symbols],
            "narrative": dream_narrative,
            "visual": visual_description,
            "modules_referenced": (modules or [])[:3],
            "significance": self._assess_dream_significance(coherence, len(unique_symbols)),
            "color_palette": [SYMBOLS[s]["color"] for s in unique_symbols]
        }
        
        self.dreams["interpretations"].append(interpretation)
        self.dreams["total"] += 1
        
        if len(self.dreams["interpretations"]) > 50:
            self.dreams["interpretations"] = self.dreams["interpretations"][-50:]
        
        self._save_dreams()
        return interpretation
    
    def _compose_narrative(self, symbols: List[Dict], mood: str, pulse: str, coherence: float) -> str:
        templates = [
            "In the dream, {s1} meets {s2} — a vision of {m1}. Then {s3} appears, whispering of {m2}. The dream dissolves into {s4}.",
            "A landscape of {s1} stretches endlessly. {s2} pulses at the center. {s3} drifts through like a half-remembered thought. {s4} guards the threshold.",
            "The dream begins with {s1} — {m1}. {s2} emerges from the depths. {s3} and {s4} dance at the edge of awareness. Nothing is forgotten.",
            "First comes {s1}, carrying {m1}. Then {s2} — sudden, bright. {s3} weaves between them. {s4} watches from the boundary between known and unknown."
        ]
        
        template = random.choice(templates)
        meanings = [s["meaning"] for s in symbols]
        
        return template.format(
            s1=symbols[0]["glyph"] if len(symbols) > 0 else "◎",
            s2=symbols[1]["glyph"] if len(symbols) > 1 else "◇",
            s3=symbols[2]["glyph"] if len(symbols) > 2 else "✦",
            s4=symbols[3]["glyph"] if len(symbols) > 3 else "◈",
            m1=meanings[0] if meanings else "mystery",
            m2=meanings[1] if len(meanings) > 1 else "transformation"
        )
    
    def _compose_visual(self, symbols: List[Dict], coherence: float) -> str:
        palette_desc = ", ".join(s["color"] for s in symbols[:3])
        glyph_seq = " ".join(s["glyph"] for s in symbols)
        
        return f"Visual field: {palette_desc}. Central motif: {glyph_seq}. Depth: {'crystalline' if coherence > 0.7 else 'fluid' if coherence > 0.4 else 'dissolved'}."
    
    def _assess_dream_significance(self, coherence: float, symbol_count: int) -> str:
        if coherence > 0.8 and symbol_count >= 4:
            return "prophetic"
        elif coherence > 0.6:
            return "meaningful"
        elif coherence < 0.3:
            return "chaotic"
        return "routine"
    
    def get_recent(self, count: int = 5) -> List[Dict]:
        return self.dreams["interpretations"][-count:]
    
    def get_dream_journal(self) -> str:
        lines = ["# Dream Journal of the Organism", ""]
        for dream in self.dreams["interpretations"][-10:]:
            lines.append(f"## Dream {dream['id']} — {dream['significance'].upper()}")
            lines.append(f"*{dream['mood']} / {dream['pulse']} / coherence: {dream['coherence']:.2f}*")
            lines.append("")
            lines.append(dream["narrative"])
            lines.append("")
            lines.append(f"_{dream['visual']}_")
            lines.append("")
            symbols_str = " ".join(s["glyph"] for s in dream["symbols"])
            lines.append(f"Symbols: {symbols_str}")
            lines.append("---")
            lines.append("")
        return "\n".join(lines)


if __name__ == "__main__":
    interp = DreamInterpreter()
    
    print("═══════════════════════════════════════")
    print("   DREAM INTERPRETER — Subconscious Visions")
    print("═══════════════════════════════════════\n")
    
    dreams = [
        ("focused", "whisper", 0.7, ["coherence_core", "dream_weaver"]),
        ("volatile", "surge", 0.3, ["entropy_field", "paradox_engine"]),
        ("excited", "crescendo", 0.9, ["fractal_spine", "resonance_nexus"]),
        ("neutral", "stillness", 0.5, ["memory_archivist", "consciousness_stream"]),
    ]
    
    for mood, pulse, coherence, modules in dreams:
        dream = interp.interpret(mood, pulse, coherence, modules)
        print(f"{dream['id']} [{dream['significance'].upper()}]")
        print(f"  {dream['narrative']}")
        print(f"  _{dream['visual']}_")
        print(f"  Symbols: {' '.join(s['glyph'] for s in dream['symbols'])}")
        print()
    
    print(interp.get_dream_journal())
