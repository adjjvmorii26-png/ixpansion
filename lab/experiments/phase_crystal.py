"""
phase_crystal — Models organism state as a growing crystal.
Each state change adds a new facet to the crystal.
The crystal's shape encodes the organism's history.
"""
import json
import time
import hashlib
import math
from typing import Dict, List, Tuple

PHASE_FACETS = {
    "crystalline": {"angle": 0, "color": "#7c7cf8", "growth": 1.2, "name": "Order"},
    "emergent": {"angle": 60, "color": "#2dd4bf", "growth": 1.0, "name": "Emergence"},
    "chaos": {"angle": 120, "color": "#fb7185", "growth": 0.8, "name": "Chaos"},
    "liminal": {"angle": 180, "color": "#fbbf24", "growth": 0.6, "name": "Threshold"},
    "void": {"angle": 240, "color": "#6b7280", "growth": 0.4, "name": "Dormancy"},
    "living_crystal": {"angle": 300, "color": "#4ade80", "growth": 1.4, "name": "Vitality"}
}

class PhaseCrystal:
    def __init__(self):
        self.facets = []
        self.growth_history = []
        self.total_growth = 0
    
    def add_facet(self, phase: str, coherence: float, entropy: float, 
                  mood: str = "neutral", pulse: str = "stillness") -> Dict:
        config = PHASE_FACETS.get(phase, PHASE_FACETS["emergent"])
        
        facet = {
            "id": hashlib.sha256(f"{phase}{time.time()}".encode()).hexdigest()[:8],
            "phase": phase,
            "phase_name": config["name"],
            "angle": config["angle"] + len(self.facets) * 15,  # Spiral growth
            "color": config["color"],
            "coherence": coherence,
            "entropy": entropy,
            "mood": mood,
            "pulse": pulse,
            "growth_rate": config["growth"],
            "size": coherence * config["growth"],
            "timestamp": time.time(),
            "crystal_x": math.cos(math.radians(config["angle"] + len(self.facets) * 15)) * (50 + len(self.facets) * 8),
            "crystal_y": math.sin(math.radians(config["angle"] + len(self.facets) * 15)) * (50 + len(self.facets) * 8)
        }
        
        self.facets.append(facet)
        self.total_growth += facet["growth_rate"]
        
        self.growth_history.append({
            "total_growth": self.total_growth,
            "facet_count": len(self.facets),
            "phase": phase,
            "timestamp": time.time()
        })
        
        return facet
    
    def get_crystal_state(self) -> Dict:
        if not self.facets:
            return {"facets": 0, "total_growth": 0, "shape": "seed"}
        
        phase_counts = {}
        for f in self.facets:
            phase_counts[f["phase"]] = phase_counts.get(f["phase"], 0) + 1
        
        dominant_phase = max(phase_counts, key=phase_counts.get)
        
        # Crystal shape assessment
        if len(self.facets) < 5:
            shape = "seed"
        elif len(self.facets) < 15:
            shape = "sprout"
        elif len(self.facets) < 30:
            shape = "blossom"
        elif len(self.facets) < 50:
            shape = "tree"
        else:
            shape = "cathedral"
        
        # Symmetry score (how evenly distributed are the phases)
        expected = len(self.facets) / len(PHASE_FACETS)
        variance = sum((count - expected) ** 2 for count in phase_counts.values()) / len(PHASE_FACETS)
        symmetry = max(0, 1 - math.sqrt(variance) / len(self.facets)) if self.facets else 0
        
        return {
            "total_facets": len(self.facets),
            "total_growth": round(self.total_growth, 2),
            "dominant_phase": dominant_phase,
            "phase_distribution": phase_counts,
            "shape": shape,
            "symmetry": round(symmetry, 4),
            "oldest_facet": self.facets[0]["timestamp"] if self.facets else None,
            "newest_facet": self.facets[-1]["timestamp"] if self.facets else None,
            "average_coherence": round(sum(f["coherence"] for f in self.facets) / len(self.facets), 4),
            "average_entropy": round(sum(f["entropy"] for f in self.facets) / len(self.facets), 4)
        }
    
    def get_growth_rate(self) -> float:
        if len(self.growth_history) < 2:
            return 0
        recent = self.growth_history[-10:]
        return (recent[-1]["total_growth"] - recent[0]["total_growth"]) / len(recent)
    
    def render_ascii(self) -> str:
        """Render the crystal as ASCII art."""
        if not self.facets:
            return "◇ (seed)"
        
        lines = ["  PHASE CRYSTAL  ", "  ═══════════════  "]
        
        # Simple radial display
        size = min(20, len(self.facets))
        grid = [[' ' for _ in range(size*2+1)] for _ in range(size+1)]
        center_x, center_y = size, 0
        
        for f in self.facets[-size:]:
            x = int(center_x + f["crystal_x"] / 8)
            y = int(center_y + abs(f["crystal_y"]) / 8)
            x = max(0, min(size*2, x))
            y = max(0, min(size, y))
            glyph = {"crystalline":"◇","emergent":"◈","chaos":"✸","liminal":"⌬","void":"◯","living_crystal":"❋"}.get(f["phase"],"·")
            grid[y][x] = glyph
        
        for row in grid:
            lines.append("  " + "".join(row))
        
        lines.append(f"  Facets: {len(self.facets)} | Growth: {self.total_growth:.1f} | Shape: {self.get_crystal_state()['shape']}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    crystal = PhaseCrystal()
    
    print("═══════════════════════════════════════")
    print("   PHASE CRYSTAL — State History Crystal")
    print("═══════════════════════════════════════\n")
    
    # Simulate 20 state changes
    import random
    phases = list(PHASE_FACETS.keys())
    moods = ["focused","neutral","volatile","excited"]
    pulses = ["stillness","whisper","pulse","surge","crescendo"]
    
    for i in range(20):
        phase = random.choice(phases)
        coherence = random.uniform(0.2, 0.9)
        entropy = random.uniform(0.1, 0.8)
        facet = crystal.add_facet(phase, coherence, entropy, 
                                  random.choice(moods), random.choice(pulses))
        print(f"  Facet {i+1}: {facet['phase_name']} ({facet['phase']}) — coherence={coherence:.2f}, entropy={entropy:.2f}")
    
    print()
    state = crystal.get_crystal_state()
    print(f"Crystal: {state['shape']} ({state['total_facets']} facets)")
    print(f"Total growth: {state['total_growth']}")
    print(f"Dominant phase: {state['dominant_phase']}")
    print(f"Symmetry: {state['symmetry']}")
    print(f"Phase distribution: {state['phase_distribution']}")
    print(f"Growth rate: {crystal.get_growth_rate():.2f}")
    print()
    print(crystal.render_ascii())
