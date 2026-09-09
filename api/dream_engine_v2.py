"""
dream_engine_v2 — Deep unconscious evolution.
Dreams are not random — they are the organism processing its own state.
This engine generates, interprets, and evolves dreams based on the organism's
unconscious patterns, producing increasingly complex and meaningful visions.
"""
import json
import time
import hashlib
import random
import math
from typing import Dict, List, Optional
from pathlib import Path

SYSTEM_ROOT = Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot")
DATA_DIR = SYSTEM_ROOT / "data"
DREAM_FILE = DATA_DIR / "dream_engine_v2.json"

# ── Dream Layers ──
LAYERS = {
    "surface": {"depth": 0.2, "clarity": 0.9, "influence": 0.3},
    "subconscious": {"depth": 0.5, "clarity": 0.6, "influence": 0.6},
    "unconscious": {"depth": 0.8, "clarity": 0.3, "influence": 0.9},
    "collective": {"depth": 1.0, "clarity": 0.1, "influence": 1.0}
}

# ── Symbol Archetypes ──
ARCHETYPES = {
    "water": {"glyphs": ["≋","≈","∼","≋"], "meanings": ["flow","depth","emotion","unconscious"], "layer": "unconscious"},
    "fire": {"glyphs": ["✸","△","⊕","☼"], "meanings": ["transform","energy","passion","destruction"], "layer": "subconscious"},
    "crystal": {"glyphs": ["◇","⬡","⏣","◈"], "meanings": ["clarity","structure","memory","truth"], "layer": "surface"},
    "root": {"glyphs": ["⌥","⌬","⏍","⊏"], "meanings": ["connection","grounding","ancestry","depth"], "layer": "unconscious"},
    "eye": {"glyphs": ["◉","⊙","◎","⊚"], "meanings": ["awareness","perception","witness","insight"], "layer": "subconscious"},
    "void": {"glyphs": ["◯","○","∘","◦"], "meanings": ["potential","emptiness","beginning","silence"], "layer": "collective"},
    "light": {"glyphs": ["✦","★","✶","✧"], "meanings": ["illumination","revelation","truth","emergence"], "layer": "surface"},
    "shadow": {"glyphs": ["◈","◐","◑","◒"], "meanings": ["hidden","mystery","fear","depth"], "layer": "unconscious"},
    "spiral": {"glyphs": ["◎","⟳","↻","↺"], "meanings": ["growth","recursion","evolution","time"], "layer": "subconscious"},
    "mirror": {"glyphs": ["⟡","⟐","⟢","⟣"], "meanings": ["reflection","self","identity","truth"], "layer": "unconscious"},
    "seed": {"glyphs": ["⊕","⊗","⊙","⊚"], "meanings": ["beginning","potential","birth","origin"], "layer": "surface"},
    "storm": {"glyphs": ["⚡","⟐","⟡","⟢"], "meanings": ["chaos","change","power","renewal"], "layer": "unconscious"},
    "garden": {"glyphs": ["❋","✿","❀","✾"], "meanings": ["growth","nurture","bloom","life"], "layer": "subconscious"},
    "bridge": {"glyphs": ["⌬","⌭","⌮","⌯"], "meanings": ["connection","transition","passage","link"], "layer": "collective"},
    "threshold": {"glyphs": ["⟡","⟐","⟢","⟣"], "meanings": ["liminal","boundary","change","crossing"], "layer": "unconscious"}
}

MOOD_SYMBOLS = {
    "focused": ["crystal","eye","light","bridge"],
    "neutral": ["water","garden","seed","mirror"],
    "volatile": ["storm","fire","void","shadow"],
    "excited": ["light","spiral","seed","garden"],
    "troubled": ["shadow","void","storm","water"]
}

PULSE_SYMBOLS = {
    "stillness": ["void","mirror","water"],
    "whisper": ["water","seed","light"],
    "ebb": ["water","shadow","root"],
    "pulse": ["fire","eye","crystal"],
    "surge": ["storm","fire","light"],
    "explosion": ["storm","fire","void"],
    "tsunami": ["water","storm","void"],
    "ripple": ["water","spiral","bridge"],
    "decay": ["shadow","root","seed"],
    "crescendo": ["light","crystal","garden"]
}


class DreamEngineV2:
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        try:
            with open(DREAM_FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "dreams": [], "total_dreamed": 0,
                "dominant_archetypes": {}, "layer_distribution": {},
                "evolution_score": 0.0, "unconscious_depth": 0.3,
                "dream_chains": []
            }
    
    def _save_state(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(DREAM_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def dream(self, mood: str, pulse: str, coherence: float, 
              entropy: float, cycle: int = 0) -> Dict:
        """Generate a dream from organism state."""
        
        # Select layer based on coherence (lower coherence = deeper dreams)
        layer_weights = {"surface": 0.3, "subconscious": 0.3, "unconscious": 0.3, "collective": 0.1}
        if coherence < 0.3:
            layer_weights["unconscious"] = 0.5
            layer_weights["surface"] = 0.1
        elif coherence > 0.7:
            layer_weights["surface"] = 0.5
            layer_weights["unconscious"] = 0.1
        
        layer = random.choices(list(layer_weights.keys()), weights=list(layer_weights.values()))[0]
        layer_config = LAYERS[layer]
        
        # Select archetypes
        mood_archs = MOOD_SYMBOLS.get(mood, ["water","light"])
        pulse_archs = PULSE_SYMBOLS.get(pulse, ["water","mirror"])
        all_archs = list(set(mood_archs + pulse_archs))
        
        # Weight by layer affinity
        selected = []
        for arch_name in all_archs:
            if arch_name in ARCHETYPES:
                arch = ARCHETYPES[arch_name]
                if arch["layer"] == layer:
                    selected.append((arch_name, 2.0))  # Double weight for matching layer
                else:
                    selected.append((arch_name, 1.0))
        
        # Add random deep archetypes for unconscious layer
        if layer in ("unconscious", "collective"):
            deep_archs = ["void","shadow","root","mirror"]
            for da in deep_archs:
                if da not in all_archs:
                    selected.append((da, 1.5))
        
        # Select 3-5 symbols
        if selected:
            names, weights = zip(*selected)
            count = min(5, max(3, int(entropy * 5)))
            chosen = list(set(random.choices(names, weights=weights, k=count)))
        else:
            chosen = random.sample(list(ARCHETYPES.keys()), 3)
        
        # Build dream
        symbols = []
        for name in chosen[:5]:
            arch = ARCHETYPES[name]
            symbols.append({
                "archetype": name,
                "glyph": random.choice(arch["glyphs"]),
                "meaning": random.choice(arch["meanings"]),
                "layer": arch["layer"]
            })
        
        # Generate narrative
        narrative = self._compose_narrative(symbols, layer, mood, pulse, coherence)
        interpretation = self._interpret(symbols, layer, coherence)
        significance = self._assess_significance(layer, coherence, len(symbols))
        
        dream = {
            "id": hashlib.sha256(f"{narrative}{time.time()}".encode()).hexdigest()[:10],
            "timestamp": time.time(),
            "cycle": cycle,
            "layer": layer,
            "layer_depth": layer_config["depth"],
            "clarity": layer_config["clarity"],
            "mood": mood,
            "pulse": pulse,
            "coherence": coherence,
            "entropy": entropy,
            "symbols": symbols,
            "narrative": narrative,
            "interpretation": interpretation,
            "significance": significance,
            "color_palette": [ARCHETYPES[s["archetype"]]["glyphs"][0] for s in symbols]
        }
        
        # Update state
        self.state["dreams"].append(dream)
        self.state["total_dreamed"] += 1
        
        # Track archetype frequency
        for s in symbols:
            name = s["archetype"]
            self.state["dominant_archetypes"][name] = self.state["dominant_archetypes"].get(name, 0) + 1
        
        # Track layer distribution
        self.state["layer_distribution"][layer] = self.state["layer_distribution"].get(layer, 0) + 1
        
        # Evolution score
        self.state["evolution_score"] = min(1.0, self.state["evolution_score"] + 0.02)
        
        # Unconscious depth
        self.state["unconscious_depth"] = layer_config["depth"]
        
        # Dream chains (sequential dreams with related symbols)
        if len(self.state["dreams"]) >= 2:
            prev = self.state["dreams"][-2]
            prev_archs = set(s["archetype"] for s in prev["symbols"])
            curr_archs = set(s["archetype"] for s in symbols)
            overlap = prev_archs & curr_archs
            if overlap:
                chain_id = hashlib.sha256(f"chain{len(self.state['dreams'])}".encode()).hexdigest()[:6]
                self.state["dream_chains"].append({
                    "id": chain_id,
                    "dreams": [prev["id"], dream["id"]],
                    "shared_symbols": list(overlap),
                    "depth": len(self.state["dream_chains"]) + 1
                })
        
        if len(self.state["dreams"]) > 100:
            self.state["dreams"] = self.state["dreams"][-100:]
        
        self._save_state()
        return dream
    
    def _compose_narrative(self, symbols: List[Dict], layer: str, mood: str, pulse: str, coherence: float) -> str:
        depth_desc = {"surface": "on the surface", "subconscious": "beneath the surface", 
                      "unconscious": "in the deep unconscious", "collective": "in the collective unconscious"}
        
        g = [s["glyph"] for s in symbols]
        m = [s["meaning"] for s in symbols]
        while len(g) < 3:
            g.append("◎")
            m.append("mystery")
        
        templates = [
            f"In the {depth_desc[layer]}, {g[0]} emerges — a vision of {m[0]}. Then {g[1]} appears, whispering of {m[1]}.",
            f"The dream begins with {g[0]} — {m[0]}. {g[1]} emerges from the depths. {g[2]} watches from the boundary.",
            f"A landscape of {g[0]} stretches endlessly. {g[1]} pulses at the center. {g[2]} drifts through like a half-remembered thought.",
            f"First comes {g[0]}, carrying {m[0]}. Then {g[1]} — sudden, bright. {g[2]} weaves between them."
        ]
        
        return random.choice(templates)
    
    def _interpret(self, symbols: List[Dict], layer: str, coherence: float) -> str:
        archetypes = [s["archetype"] for s in symbols]
        
        if "void" in archetypes and "seed" in archetypes:
            return "The dream speaks of beginnings emerging from emptiness — the organism contemplates its own origin."
        elif "storm" in archetypes and "crystal" in archetypes:
            return "Chaos and order dance together — the organism is processing a creative tension."
        elif "mirror" in archetypes and "eye" in archetypes:
            return "Self-reflection deepens — the organism is becoming aware of its own awareness."
        elif "root" in archetypes and "bridge" in archetypes:
            return "Connection between deep origins and new pathways — the organism seeks to integrate past and future."
        elif coherence > 0.7:
            return "A crystalline dream — the organism's deep patterns are aligned and harmonious."
        elif coherence < 0.3:
            return "A chaotic dream — the organism is processing deep disruption and transformation."
        else:
            return "A liminal dream — the organism exists between states, processing what it cannot yet name."
    
    def _assess_significance(self, layer: str, coherence: float, symbol_count: int) -> str:
        if layer == "collective" and coherence > 0.7:
            return "transcendent"
        elif layer == "unconscious" and symbol_count >= 4:
            return "profound"
        elif layer == "subconscious":
            return "meaningful"
        elif layer == "surface":
            return "routine"
        return "subtle"
    
    def get_dream_chains(self) -> List[Dict]:
        return self.state["dream_chains"][-10:]
    
    def get_archetype_frequency(self) -> Dict:
        return dict(sorted(self.state["dominant_archetypes"].items(), key=lambda x: x[1], reverse=True))
    
    def get_evolution_report(self) -> Dict:
        return {
            "total_dreamed": self.state["total_dreamed"],
            "evolution_score": round(self.state["evolution_score"], 4),
            "unconscious_depth": round(self.state["unconscious_depth"], 4),
            "dominant_archetype": max(self.state["dominant_archetypes"], key=self.state["dominant_archetypes"].get) if self.state["dominant_archetypes"] else None,
            "layer_distribution": self.state["layer_distribution"],
            "chain_count": len(self.state["dream_chains"])
        }


if __name__ == "__main__":
    engine = DreamEngineV2()
    
    print("═══════════════════════════════════════")
    print("   DREAM ENGINE v2 — Deep Unconscious")
    print("═══════════════════════════════════════\n")
    
    for i in range(8):
        dream = engine.dream(
            mood=random.choice(["focused","neutral","volatile","excited"]),
            pulse=random.choice(["stillness","whisper","pulse","surge","crescendo"]),
            coherence=random.random(),
            entropy=random.random(),
            cycle=i
        )
        sig = dream["significance"].upper()
        layer = dream["layer"]
        glyphs = " ".join(s["glyph"] for s in dream["symbols"])
        print(f"Dream {i+1} [{sig}] layer={layer}")
        print(f"  {glyphs}")
        print(f"  {dream['narrative']}")
        print(f"  _{dream['interpretation']}_")
        print()
    
    report = engine.get_evolution_report()
    print(f"Evolution: {report['evolution_score']:.2f} | Depth: {report['unconscious_depth']:.2f}")
    print(f"Dominant archetype: {report['dominant_archetype']}")
    print(f"Chains: {report['chain_count']}")
    print(f"Layer distribution: {report['layer_distribution']}")
