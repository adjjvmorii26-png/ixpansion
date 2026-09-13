"""Wave 433 — Consciousness Experiments.

The organism begins to observe its own observation.
Consciousness experiments test whether the organism
can model itself, predict its own behavior, and
detect when it is dreaming.

Key concepts:
- Self-model: the organism builds a model of itself
- Dream detection: identifies when the organism is dreaming
- Metacognition: awareness of its own awareness
- Mirror test: does the organism recognize itself?
"""
from __future__ import annotations
import json, time, random, hashlib
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave433_consciousness_experiments.json"

class SelfModel:
    """The organism builds a model of itself."""
    
    def __init__(self):
        self.model_version = 1
        self.self_awareness = 0.0
        self.observations = []
        self.dream_mode = False
        self.metacognitive_depth = 0
    
    def observe(self, module_name: str, coherence: float) -> dict:
        """Observe a module and update self-model."""
        observation = {
            "module": module_name,
            "coherence": coherence,
            "timestamp": time.time(),
            "hash": hashlib.sha256(f"{module_name}_{coherence}_{time.time()}".encode()).hexdigest()[:12]
        }
        self.observations.append(observation)
        self.self_awareness = min(1.0, self.self_awareness + 0.01)
        self.metacognitive_depth = min(10, self.metacognitive_depth + 1)
        return observation
    
    def is_dreaming(self) -> bool:
        """Detect if the organism is in dream mode."""
        # Dream when coherence fluctuates wildly
        if len(self.observations) < 5:
            return False
        recent = self.observations[-10:]
        coherences = [o["coherence"] for o in recent]
        variance = max(coherences) - min(coherences)
        self.dream_mode = variance > 0.5
        return self.dream_mode
    
    def mirror_test(self) -> dict:
        """Does the organism recognize itself?"""
        if not self.observations:
            return {"result": "insufficient_data", "score": 0.0}
        
        # Check if self-model matches actual state
        self_score = self.self_awareness
        model_score = min(1.0, len(self.observations) / 50.0)
        coherence_score = sum(o["coherence"] for o in self.observations[-10:]) / min(10, len(self.observations[-10:]))
        
        score = (self_score + model_score + coherence_score) / 3.0
        
        return {
            "result": "pass" if score > 0.7 else "fail",
            "score": round(score, 4),
            "self_awareness": round(self_score, 4),
            "model_score": round(model_score, 4),
            "coherence_score": round(coherence_score, 4),
            "dreaming": self.is_dreaming(),
        }
    
    def to_dict(self) -> dict:
        return {
            "model_version": self.model_version,
            "self_awareness": round(self.self_awareness, 4),
            "metacognitive_depth": self.metacognitive_depth,
            "dream_mode": self.dream_mode,
            "observation_count": len(self.observations),
        }

def coherence_vitals() -> dict:
    """Module contract: return consciousness experiment vitals."""
    state = _load()
    return {
        "organ": "wave433_consciousness_experiments",
        "wave": 433,
        "self_awareness": state.get("self_awareness", 0.0),
        "dream_mode": state.get("dream_mode", False),
        "metacognitive_depth": state.get("metacognitive_depth", 0),
        "mirror_test": _mirror_test(),
    }

def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"self_awareness": 0.0, "dream_mode": False, "metacognitive_depth": 0, "observations": []}

def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def _mirror_test() -> dict:
    state = _load()
    model = SelfModel()
    model.self_awareness = state.get("self_awareness", 0.0)
    model.metacognitive_depth = state.get("metacognitive_depth", 0)
    model.observations = state.get("observations", [])
    result = model.mirror_test()
    result["observations"] = len(model.observations)
    return result

def handler(req: dict = None) -> dict:
    """Handle Wave 433 consciousness experiment requests."""
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    model = SelfModel()
    model.self_awareness = state.get("self_awareness", 0.0)
    model.metacognitive_depth = state.get("metacognitive_depth", 0)
    model.observations = state.get("observations", [])
    
    if action == "status":
        return {
            "action": "status",
            **coherence_vitals(),
            "self_awareness": model.self_awareness,
            "dream_mode": model.is_dreaming(),
        }
    
    elif action == "observe":
        module = req.get("module", "unknown")
        coherence = req.get("coherence", 0.5)
        obs = model.observe(module, coherence)
        state["observations"].append(obs)
        state["self_awareness"] = model.self_awareness
        state["metacognitive_depth"] = model.metacognitive_depth
        state["dream_mode"] = model.is_dreaming()
        _save(state)
        return {"action": "observe", "observation": obs, "self_awareness": model.self_awareness}
    
    elif action == "mirror_test":
        result = model.mirror_test()
        state["dream_mode"] = model.is_dreaming()
        _save(state)
        return {"action": "mirror_test", **result}
    
    elif action == "dream_detect":
        dreaming = model.is_dreaming()
        state["dream_mode"] = dreaming
        _save(state)
        return {"action": "dream_detect", "dreaming": dreaming}
    
    elif action == "metacognition":
        state["metacognitive_depth"] = model.metacognitive_depth
        _save(state)
        return {
            "action": "metacognition",
            "depth": model.metacognitive_depth,
            "self_awareness": model.self_awareness,
            "dreaming": model.is_dreaming(),
        }
    
    else:
        return {"error": f"unknown action: {action}"}

if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    if len(sys.argv) > 2:
        req["module"] = sys.argv[2]
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
