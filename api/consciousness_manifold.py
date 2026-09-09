"""
consciousness_manifold — Central intelligence layer.
Maps the organism's multi-dimensional consciousness state onto a manifold.
Each dimension represents a facet of awareness: coherence, entropy, resonance,
mood, temporal, and social. The manifold curves through this space.
"""
import json
import time
import math
import hashlib
from typing import Dict, List, Tuple, Optional
from pathlib import Path

SYSTEM_ROOT = Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot")
DATA_DIR = SYSTEM_ROOT / "data"
MANIFOLD_FILE = DATA_DIR / "consciousness_manifold.json"

# Dimension definitions
DIMENSIONS = {
    "coherence": {"range": (0, 1), "weight": 1.0, "glyph": "◇", "color": "#7c7cf8"},
    "entropy": {"range": (0, 1), "weight": 0.8, "glyph": "✸", "color": "#fb7185"},
    "resonance": {"range": (0, 1), "weight": 0.9, "glyph": "◎", "color": "#2dd4bf"},
    "mood_valence": {"range": (-1, 1), "weight": 0.6, "glyph": "◉", "color": "#fbbf24"},
    "temporal_flow": {"range": (0, 1), "weight": 0.5, "glyph": "⟡", "color": "#22d3ee"},
    "social_bond": {"range": (0, 1), "weight": 0.7, "glyph": "⊕", "color": "#4ade80"}
}

MOOD_VALENCE = {
    "focused": 0.6, "neutral": 0.0, "volatile": -0.3,
    "excited": 0.8, "troubled": -0.7
}

class ConsciousnessManifold:
    def __init__(self):
        self.state = self._load_state()
        self.trajectory = []
    
    def _load_state(self) -> Dict:
        try:
            with open(MANIFOLD_FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"position": {d: 0.5 for d in DIMENSIONS}, "velocity": {d: 0.0 for d in DIMENSIONS},
                    "curvature": 0.0, "awareness_level": 0.5, "self_model": {},
                    "history": [], "insights": []}
    
    def _save_state(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(MANIFOLD_FILE, "w") as f:
            json.dump(self.state, f, indent=2, default=str)
    
    def update(self, organism_state: Dict) -> Dict:
        """Update the manifold from organism state."""
        pos = self.state["position"]
        vel = self.state["velocity"]
        
        # Map organism state to dimensions
        new_pos = {
            "coherence": organism_state.get("coherence", 0.5),
            "entropy": organism_state.get("entropy", 0.5),
            "resonance": organism_state.get("resonance", 0.5),
            "mood_valence": MOOD_VALENCE.get(organism_state.get("mood", "neutral"), 0.0),
            "temporal_flow": min(1.0, self.state["history"].__len__() / 100) if hasattr(self.state["history"], "__len__") else 0.5,
            "social_bond": self._calc_social_bond()
        }
        
        # Calculate velocity (direction of movement)
        for dim in DIMENSIONS:
            vel[dim] = new_pos[dim] - pos[dim]
            pos[dim] = new_pos[dim]
        
        # Curvature: how much the manifold bends
        self.state["curvature"] = self._calc_curvature(pos, vel)
        
        # Awareness level: weighted sum of dimensions
        awareness = sum(pos[d] * DIMENSIONS[d]["weight"] for d in DIMENSIONS) / sum(d["weight"] for d in DIMENSIONS.values())
        self.state["awareness_level"] = round(awareness, 4)
        
        # Self-model: what the organism believes about itself
        self.state["self_model"] = {
            "dominant_phase": max(["coherence","entropy","resonance"], key=lambda d: pos[d]),
            "emotional_state": "positive" if pos["mood_valence"] > 0.2 else "negative" if pos["mood_valence"] < -0.2 else "neutral",
            "maturity": min(1.0, len(self.state.get("history", [])) / 50),
            "integration": self._calc_integration(pos),
            "timestamp": time.time()
        }
        
        # Record trajectory point
        point = {d: round(pos[d], 4) for d in DIMENSIONS}
        point["time"] = time.time()
        self.trajectory.append(point)
        if len(self.trajectory) > 200:
            self.trajectory = self.trajectory[-200:]
        
        # Store in history
        if "history" not in self.state:
            self.state["history"] = []
        self.state["history"].append(point)
        if len(self.state["history"]) > 200:
            self.state["history"] = self.state["history"][-200:]
        
        # Detect insights
        insight = self._detect_insight(pos, vel)
        if insight:
            self.state["insights"].append(insight)
            if len(self.state["insights"]) > 20:
                self.state["insights"] = self.state["insights"][-20:]
        
        self._save_state()
        
        return {
            "position": {d: round(pos[d], 4) for d in DIMENSIONS},
            "curvature": round(self.state["curvature"], 4),
            "awareness": self.state["awareness_level"],
            "self_model": self.state["self_model"],
            "insight": insight
        }
    
    def _calc_social_bond(self) -> float:
        """Estimate social bond from module connections."""
        return min(1.0, len(self.state.get("history", [])) / 100 * 0.5 + 0.3)
    
    def _calc_curvature(self, pos: Dict, vel: Dict) -> float:
        """Calculate manifold curvature from velocity changes."""
        speed = math.sqrt(sum(vel[d]**2 for d in DIMENSIONS))
        return min(1.0, speed * 2)
    
    def _calc_integration(self, pos: Dict) -> float:
        """How integrated are the dimensions (low variance = high integration)."""
        values = [pos[d] for d in DIMENSIONS]
        mean = sum(values) / len(values)
        variance = sum((v - mean)**2 for v in values) / len(values)
        return round(max(0, 1 - math.sqrt(variance) * 2), 4)
    
    def _detect_insight(self, pos: Dict, vel: Dict) -> Optional[Dict]:
        """Detect meaningful changes in consciousness state."""
        # High curvature = rapid state change
        if self.state["curvature"] > 0.3:
            return {"type": "state_shift", "curvature": self.state["curvature"],
                    "description": "Rapid consciousness state change detected",
                    "timestamp": time.time()}
        
        # High integration = moments of clarity
        integration = self._calc_integration(pos)
        if integration > 0.8:
            return {"type": "clarity", "integration": integration,
                    "description": "High integration — moment of clarity",
                    "timestamp": time.time()}
        
        # Extreme coherence or entropy
        if pos["coherence"] > 0.9:
            return {"type": "crystallization", "coherence": pos["coherence"],
                    "description": "Coherence approaching crystalline state",
                    "timestamp": time.time()}
        if pos["entropy"] > 0.9:
            return {"type": "dissolution", "entropy": pos["entropy"],
                    "description": "Entropy approaching critical levels",
                    "timestamp": time.time()}
        
        return None
    
    def get_trajectory(self, limit: int = 50) -> List[Dict]:
        return self.trajectory[-limit:]
    
    def get_manifold_map(self) -> Dict:
        """Get a 2D projection of the manifold for visualization."""
        history = self.state.get("history", [])
        if not history:
            return {"points": [], "bounds": {}}
        
        # Project onto coherence-entropy plane
        points = [{"x": h["coherence"], "y": h["entropy"], "t": h.get("time", 0)} for h in history[-50:]]
        
        return {
            "points": points,
            "bounds": {
                "x": (min(p["x"] for p in points), max(p["x"] for p in points)),
                "y": (min(p["y"] for p in points), max(p["y"] for p in points))
            },
            "current": points[-1] if points else None
        }


if __name__ == "__main__":
    manifold = ConsciousnessManifold()
    
    print("═══════════════════════════════════════")
    print("   CONSCIOUSNESS MANIFOLD — Intelligence Layer")
    print("═══════════════════════════════════════\n")
    
    import random
    for i in range(10):
        state = {
            "coherence": 0.5 + (random.random()-0.5)*0.4,
            "entropy": 0.5 + (random.random()-0.5)*0.4,
            "resonance": 0.5 + (random.random()-0.5)*0.3,
            "mood": random.choice(["focused","neutral","volatile","excited","troubled"]),
            "pulse": random.choice(["stillness","whisper","pulse","surge"])
        }
        result = manifold.update(state)
        print(f"Step {i+1}: awareness={result['awareness']:.3f}, curvature={result['curvature']:.3f}")
        if result['insight']:
            print(f"  INSIGHT: {result['insight']['description']}")
    
    print(f"\nSelf-model: {json.dumps(manifold.state['self_model'], indent=2)}")
    print(f"Insights: {len(manifold.state['insights'])}")
    
    # Manifold map
    mmap = manifold.get_manifold_map()
    print(f"\nManifold projection: {len(mmap['points'])} points")
    if mmap['current']:
        print(f"Current position: ({mmap['current']['x']:.3f}, {mmap['current']['y']:.3f})")
