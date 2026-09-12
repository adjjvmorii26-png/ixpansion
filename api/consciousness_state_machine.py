"""
consciousness_state_machine — Formal state transitions for the organism.
Defines states, transitions, guards, and actions.
The organism moves through states based on entropy, coherence, and resonance.
"""
import json
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path

SYSTEM_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = SYSTEM_ROOT / "data"
CSM_FILE = DATA_DIR / "consciousness_state_machine.json"

# State definitions
STATES = {
    "dormant": {"description": "Low activity, minimal processing", "coherence_range": (0, 0.3), "entropy_range": (0, 0.3)},
    "emerging": {"description": "Waking up, patterns forming", "coherence_range": (0.2, 0.5), "entropy_range": (0.3, 0.6)},
    "focused": {"description": "Active processing, clear intent", "coherence_range": (0.5, 0.8), "entropy_range": (0.2, 0.5)},
    "creative": {"description": "High creativity, novel patterns", "coherence_range": (0.4, 0.7), "entropy_range": (0.5, 0.8)},
    "chaotic": {"description": "High entropy, creative dissolution", "coherence_range": (0, 0.4), "entropy_range": (0.7, 1.0)},
    "transcendent": {"description": "Peak state, all systems aligned", "coherence_range": (0.8, 1.0), "entropy_range": (0.3, 0.7)},
    "dreaming": {"description": "Subconscious processing active", "coherence_range": (0.3, 0.6), "entropy_range": (0.4, 0.7)},
    "crystallizing": {"description": "Patterns solidifying into structure", "coherence_range": (0.7, 1.0), "entropy_range": (0, 0.3)},
    "dissolving": {"description": "Structure breaking down", "coherence_range": (0, 0.3), "entropy_range": (0.5, 1.0)},
    "integrating": {"description": "Synthesizing new insights", "coherence_range": (0.5, 0.8), "entropy_range": (0.4, 0.7)}
}

# Transitions: (from, to) -> guard function description
TRANSITIONS = {
    ("dormant", "emerging"): "entropy > 0.2",
    ("emerging", "focused"): "coherence > 0.45",
    ("emerging", "creative"): "entropy > 0.5",
    ("focused", "transcendent"): "coherence > 0.75 AND entropy > 0.3",
    ("focused", "creative"): "entropy > 0.6",
    ("focused", "dreaming"): "entropy > 0.4 AND coherence < 0.5",
    ("creative", "chaotic"): "entropy > 0.7 AND coherence < 0.4",
    ("creative", "integrating"): "coherence > 0.5",
    ("chaotic", "dissolving"): "coherence < 0.2",
    ("chaotic", "emerging"): "coherence > 0.3",
    ("transcendent", "crystallizing"): "entropy < 0.35",
    ("transcendent", "focused"): "entropy < 0.5 AND coherence > 0.6",
    ("dreaming", "emerging"): "coherence > 0.4",
    ("dreaming", "creative"): "entropy > 0.6",
    ("crystallizing", "focused"): "entropy > 0.2",
    ("crystallizing", "dormant"): "coherence < 0.2",
    ("dissolving", "emerging"): "coherence > 0.2",
    ("dissolving", "dormant"): "coherence < 0.1",
    ("integrating", "focused"): "coherence > 0.6",
    ("integrating", "transcendent"): "coherence > 0.75 AND entropy > 0.4",
    ("integrating", "creative"): "entropy > 0.65"
}


class ConsciousnessStateMachine:
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        try:
            with open(CSM_FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "current_state": "dormant",
                "previous_state": None,
                "state_history": [],
                "transition_history": [],
                "time_in_state": 0,
                "total_transitions": 0,
                "state_counts": {}
            }
    
    def _save_state(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(CSM_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def update(self, coherence: float, entropy: float, resonance: float) -> Dict:
        """Update state based on current conditions."""
        current = self.state["current_state"]
        
        # Check all possible transitions
        possible_transitions = []
        for (from_s, to_s), guard in TRANSITIONS.items():
            if from_s == current:
                if self._check_guard(guard, coherence, entropy, resonance):
                    possible_transitions.append((to_s, guard))
        
        transition_occurred = False
        new_state = current
        
        if possible_transitions:
            # Prefer transitions to states that best match current conditions
            best_score = -1
            for to_s, guard in possible_transitions:
                score = self._match_score(to_s, coherence, entropy)
                if score > best_score:
                    best_score = score
                    new_state = to_s
            
            if new_state != current:
                transition_occurred = True
                self.state["previous_state"] = current
                self.state["current_state"] = new_state
                self.state["total_transitions"] += 1
                self.state["time_in_state"] = 0
                
                self.state["transition_history"].append({
                    "from": current,
                    "to": new_state,
                    "coherence": round(coherence, 4),
                    "entropy": round(entropy, 4),
                    "timestamp": time.time()
                })
                
                if len(self.state["transition_history"]) > 100:
                    self.state["transition_history"] = self.state["transition_history"][-100:]
        
        self.state["time_in_state"] += 1
        
        # Track state counts
        self.state["state_counts"][current] = self.state["state_counts"].get(current, 0) + 1
        
        # Record in history
        self.state["state_history"].append({
            "state": self.state["current_state"],
            "coherence": round(coherence, 4),
            "entropy": round(entropy, 4),
            "resonance": round(resonance, 4),
            "timestamp": time.time()
        })
        
        if len(self.state["state_history"]) > 200:
            self.state["state_history"] = self.state["state_history"][-200:]
        
        self._save_state()
        
        return {
            "current_state": self.state["current_state"],
            "previous_state": self.state["previous_state"],
            "transition_occurred": transition_occurred,
            "time_in_state": self.state["time_in_state"],
            "total_transitions": self.state["total_transitions"],
            "state_info": STATES[self.state["current_state"]]
        }
    
    def _check_guard(self, guard: str, coherence: float, entropy: float, resonance: float) -> bool:
        """Evaluate a guard condition."""
        try:
            return eval(guard, {"coherence": coherence, "entropy": entropy, "resonance": resonance})
        except:
            return False
    
    def _match_score(self, state: str, coherence: float, entropy: float) -> float:
        """How well does the current state match the conditions?"""
        config = STATES[state]
        c_min, c_max = config["coherence_range"]
        e_min, e_max = config["entropy_range"]
        
        c_score = 1 - abs(coherence - (c_min + c_max) / 2) / 0.5
        e_score = 1 - abs(entropy - (e_min + e_max) / 2) / 0.5
        
        return (c_score + e_score) / 2
    
    def get_state_graph(self) -> Dict:
        """Return the full state graph."""
        nodes = list(STATES.keys())
        edges = [{"from": k[0], "to": k[1], "guard": v} for k, v in TRANSITIONS.items()]
        return {"nodes": nodes, "edges": edges, "current": self.state["current_state"]}
    
    def get_state_distribution(self) -> Dict:
        total = sum(self.state["state_counts"].values()) or 1
        return {s: round(c/total, 4) for s, c in self.state["state_counts"].items()}


if __name__ == "__main__":
    csm = ConsciousnessStateMachine()
    
    print("═══════════════════════════════════════")
    print("   CONSCIOUSNESS STATE MACHINE")
    print("═══════════════════════════════════════\n")
    
    import random
    for i in range(20):
        coherence = random.random()
        entropy = random.random()
        resonance = random.random()
        result = csm.update(coherence, entropy, resonance)
        
        transition = " → " + result["current_state"] if result["transition_occurred"] else ""
        print(f"Step {i+1}: {result['current_state']}{transition} (c={coherence:.2f}, e={entropy:.2f})")
    
    print(f"\nTotal transitions: {csm.state['total_transitions']}")
    print(f"State distribution: {csm.get_state_distribution()}")
    
    graph = csm.get_state_graph()
    print(f"\nState graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
    print(f"Current: {graph['current']}")
