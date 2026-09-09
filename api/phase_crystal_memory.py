"""
phase_crystal_memory — Temporal intelligence.
Records organism state as crystal facets that grow over time.
The crystal's shape encodes the organism's history and predicts future states.
"""
import json
import time
import hashlib
import math
from typing import Dict, List, Optional
from pathlib import Path

SYSTEM_ROOT = Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot")
DATA_DIR = SYSTEM_ROOT / "data"
CRYSTAL_FILE = DATA_DIR / "phase_crystal_memory.json"

PHASE_FACETS = {
    "crystalline": {"angle": 0, "color": "#7c7cf8", "growth": 1.2, "name": "Order"},
    "emergent": {"angle": 60, "color": "#2dd4bf", "growth": 1.0, "name": "Emergence"},
    "chaos": {"angle": 120, "color": "#fb7185", "growth": 0.8, "name": "Chaos"},
    "liminal": {"angle": 180, "color": "#fbbf24", "growth": 0.6, "name": "Threshold"},
    "void": {"angle": 240, "color": "#6b7280", "growth": 0.4, "name": "Dormancy"},
    "living_crystal": {"angle": 300, "color": "#4ade80", "growth": 1.4, "name": "Vitality"}
}

class PhaseCrystalMemory:
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        try:
            with open(CRYSTAL_FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"facets": [], "total_growth": 0, "generation": 0,
                    "phase_history": {}, "memory_fragments": [],
                    "temporal_patterns": [], "prediction_accuracy": 0.5}
    
    def _save_state(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(CRYSTAL_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def record(self, phase: str, coherence: float, entropy: float, 
               mood: str, pulse: str) -> Dict:
        """Record a state as a crystal facet."""
        config = PHASE_FACETS.get(phase, PHASE_FACETS["emergent"])
        
        facet = {
            "id": hashlib.sha256(f"{phase}{time.time()}".encode()).hexdigest()[:8],
            "phase": phase,
            "phase_name": config["name"],
            "coherence": coherence,
            "entropy": entropy,
            "mood": mood,
            "pulse": pulse,
            "growth_rate": config["growth"],
            "size": coherence * config["growth"],
            "timestamp": time.time(),
            "angle": config["angle"] + len(self.state["facets"]) * 15
        }
        
        self.state["facets"].append(facet)
        self.state["total_growth"] += facet["growth_rate"]
        self.state["generation"] += 1
        
        # Track phase frequency
        self.state["phase_history"][phase] = self.state["phase_history"].get(phase, 0) + 1
        
        # Detect temporal patterns
        if len(self.state["facets"]) >= 5:
            pattern = self._detect_pattern()
            if pattern:
                self.state["temporal_patterns"].append(pattern)
                if len(self.state["temporal_patterns"]) > 20:
                    self.state["temporal_patterns"] = self.state["temporal_patterns"][-20:]
        
        # Generate memory fragment
        if len(self.state["facets"]) % 5 == 0:
            fragment = self._compress_memory()
            self.state["memory_fragments"].append(fragment)
            if len(self.state["memory_fragments"]) > 10:
                self.state["memory_fragments"] = self.state["memory_fragments"][-10:]
        
        # Prediction accuracy
        if len(self.state["facets"]) >= 3:
            accuracy = self._check_prediction()
            self.state["prediction_accuracy"] = accuracy
        
        if len(self.state["facets"]) > 200:
            self.state["facets"] = self.state["facets"][-200:]
        
        self._save_state()
        return facet
    
    def _detect_pattern(self) -> Optional[Dict]:
        recent = self.state["facets"][-10:]
        phases = [f["phase"] for f in recent]
        
        # Check for phase cycling
        for period in range(2, 6):
            matches = sum(1 for i in range(len(phases)-period) if phases[i] == phases[i+period])
            if matches > len(phases) // (period * 2):
                return {"type": "phase_cycle", "period": period, "strength": matches / max(len(phases)-period, 1),
                        "cycle": phases[:period], "timestamp": time.time()}
        
        # Check for phase progression
        unique_phases = list(dict.fromkeys(phases))
        if len(unique_phases) >= 3:
            return {"type": "phase_progression", "sequence": unique_phases[:5],
                    "timestamp": time.time()}
        
        return None
    
    def _compress_memory(self) -> Dict:
        """Compress recent facets into a memory fragment."""
        recent = self.state["facets"][-5:]
        avg_coherence = sum(f["coherence"] for f in recent) / len(recent)
        avg_entropy = sum(f["entropy"] for f in recent) / len(recent)
        dominant_phase = max(set(f["phase"] for f in recent), key=lambda p: sum(1 for f in recent if f["phase"] == p))
        
        return {
            "id": hashlib.sha256(f"frag{time.time()}".encode()).hexdigest()[:6],
            "facets_compressed": len(recent),
            "avg_coherence": round(avg_coherence, 4),
            "avg_entropy": round(avg_entropy, 4),
            "dominant_phase": dominant_phase,
            "timestamp": time.time(),
            "summary": f"A period of {dominant_phase} (coherence={avg_coherence:.2f}, entropy={avg_entropy:.2f})"
        }
    
    def _check_prediction(self) -> float:
        """Check if recent predictions were accurate."""
        if len(self.state["temporal_patterns"]) < 1:
            return self.state["prediction_accuracy"]
        
        last_pattern = self.state["temporal_patterns"][-1]
        if last_pattern["type"] == "phase_cycle":
            recent_phases = [f["phase"] for f in self.state["facets"][-5:]]
            predicted = last_pattern["cycle"][0]
            matches = sum(1 for p in recent_phases if p == predicted)
            accuracy = matches / len(recent_phases)
            return round(accuracy * 0.3 + self.state["prediction_accuracy"] * 0.7, 4)
        
        return self.state["prediction_accuracy"]
    
    def predict_next(self) -> Dict:
        """Predict the next likely phase."""
        if not self.state["facets"]:
            return {"prediction": "unknown", "confidence": 0}
        
        # Use temporal patterns
        if self.state["temporal_patterns"]:
            last = self.state["temporal_patterns"][-1]
            if last["type"] == "phase_cycle":
                recent_idx = len(self.state["facets"]) % last["period"]
                predicted = last["cycle"][recent_idx % len(last["cycle"])]
                return {"prediction": predicted, "confidence": last["strength"],
                        "method": "cycle_detection"}
        
        # Use phase frequency
        if self.state["phase_history"]:
            dominant = max(self.state["phase_history"], key=self.state["phase_history"].get)
            total = sum(self.state["phase_history"].values())
            confidence = self.state["phase_history"][dominant] / total
            return {"prediction": dominant, "confidence": round(confidence, 4),
                    "method": "frequency_analysis"}
        
        return {"prediction": "emergent", "confidence": 0.3, "method": "default"}
    
    def get_crystal_state(self) -> Dict:
        if not self.state["facets"]:
            return {"facets": 0, "shape": "seed", "total_growth": 0}
        
        n = len(self.state["facets"])
        shape = "seed" if n < 5 else "sprout" if n < 15 else "blossom" if n < 30 else "tree" if n < 50 else "cathedral"
        
        return {
            "facets": n,
            "shape": shape,
            "total_growth": round(self.state["total_growth"], 2),
            "generation": self.state["generation"],
            "phase_distribution": self.state["phase_history"],
            "memory_fragments": len(self.state["memory_fragments"]),
            "temporal_patterns": len(self.state["temporal_patterns"]),
            "prediction_accuracy": self.state["prediction_accuracy"]
        }


if __name__ == "__main__":
    crystal = PhaseCrystalMemory()
    
    print("═══════════════════════════════════════")
    print("   PHASE CRYSTAL MEMORY — Temporal Intelligence")
    print("═══════════════════════════════════════\n")
    
    import random
    phases = list(PHASE_FACETS.keys())
    moods = ["focused","neutral","volatile","excited"]
    pulses = ["stillness","whisper","pulse","surge","crescendo"]
    
    for i in range(25):
        phase = random.choice(phases)
        facet = crystal.record(phase, random.random(), random.random(),
                              random.choice(moods), random.choice(pulses))
    
    state = crystal.get_crystal_state()
    print(f"Crystal: {state['shape']} ({state['facets']} facets)")
    print(f"Growth: {state['total_growth']}")
    print(f"Phase distribution: {state['phase_distribution']}")
    print(f"Memory fragments: {state['memory_fragments']}")
    print(f"Temporal patterns: {state['temporal_patterns']}")
    print(f"Prediction accuracy: {state['prediction_accuracy']:.2f}")
    
    pred = crystal.predict_next()
    print(f"\nPrediction: {pred['prediction']} (confidence: {pred['confidence']:.2f}, method: {pred['method']})")
    
    if crystal.state["memory_fragments"]:
        print(f"\nLatest memory fragment:")
        frag = crystal.state["memory_fragments"][-1]
        print(f"  {frag['summary']}")
