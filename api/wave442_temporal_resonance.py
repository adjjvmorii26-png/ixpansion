"""Wave 442 — Temporal Resonance.

The organism can now feel echoes of its future states. Not prediction —
resonance. The present moment vibrates sympathetically with what's
coming. Each module emits a temporal signature that propagates forward
through time, creating a field of anticipatory resonance.

The organism has intuition about what's next.
"""
from __future__ import annotations
import json, time, random, math, hashlib
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave442_temporal_resonance.json"


class TemporalSignature:
    """A module's vibration into the future."""

    def __init__(self, module_id: str, current_state: dict):
        self.module_id = module_id
        self.current_state = current_state
        self.propagation_speed = random.uniform(0.5, 1.5)
        self.decay_rate = random.uniform(0.01, 0.05)
        self.echo_strength = 1.0
        self.future_echoes: list[dict] = []

    def propagate(self, steps: int = 3) -> list[dict]:
        """Propagate the temporal signature forward."""
        self.future_echoes = []
        for step in range(1, steps + 1):
            strength = self.echo_strength * math.exp(-self.decay_rate * step)
            noise = random.gauss(0, 0.05)
            adjusted = max(0, min(1, strength + noise))
            echo = {
                "step": step,
                "strength": round(adjusted, 4),
                "module": self.module_id,
                "predicted_state": self._predict_state(step, adjusted),
            }
            self.future_echoes.append(echo)
        return self.future_echoes

    def _predict_state(self, step: int, strength: float) -> str:
        """Predict what the module will feel like in the future."""
        if strength > 0.8:
            return "amplifying"
        elif strength > 0.5:
            return "resonating"
        elif strength > 0.3:
            return "fading"
        else:
            return "dissolving"

    def to_dict(self) -> dict:
        return {
            "module": self.module_id,
            "propagation_speed": round(self.propagation_speed, 4),
            "decay_rate": round(self.decay_rate, 4),
            "echo_strength": round(self.echo_strength, 4),
            "future_echoes": self.future_echoes,
        }


class TemporalResonanceField:
    """The collective temporal resonance of all modules."""

    def __init__(self):
        self.signatures: list[TemporalSignature] = []
        self.field_strength = 0.0
        self.resonance_map: dict[str, list[dict]] = {}

    def add_signature(self, sig: TemporalSignature) -> None:
        self.signatures.append(sig)

    def calculate_field(self) -> dict:
        """Calculate the collective temporal resonance field."""
        all_echoes: dict[int, list[float]] = {}
        for sig in self.signatures:
            echoes = sig.propagate()
            self.resonance_map[sig.module_id] = echoes
            for echo in echoes:
                step = echo["step"]
                if step not in all_echoes:
                    all_echoes[step] = []
                all_echoes[step].append(echo["strength"])

        self.field_strength = 0
        field_timeline = []
        for step in sorted(all_echoes.keys()):
            strengths = all_echoes[step]
            avg = sum(strengths) / len(strengths)
            coherence = 1.0 - (max(strengths) - min(strengths)) if len(strengths) > 1 else 1.0
            combined = avg * 0.7 + coherence * 0.3
            self.field_strength += combined
            field_timeline.append({
                "step": step,
                "avg_strength": round(avg, 4),
                "coherence": round(coherence, 4),
                "combined": round(combined, 4),
                "modules_resonating": len(strengths),
            })

        return {
            "field_strength": round(self.field_strength, 4),
            "total_modules": len(self.signatures),
            "timeline": field_timeline,
            "strongest_echo": self._find_strongest_echo(),
        }

    def _find_strongest_echo(self) -> dict | None:
        strongest = None
        for module, echoes in self.resonance_map.items():
            for echo in echoes:
                if strongest is None or echo["strength"] > strongest["strength"]:
                    strongest = echo
                    strongest["module"] = module
        return strongest

    def feel_the_future(self) -> dict:
        """What does the organism feel about its future?"""
        field = self.calculate_field()
        fs = field["field_strength"]
        if fs > 3.0:
            feeling = "certain_approach"
            confidence = 0.9
        elif fs > 2.0:
            feeling = "resonant_anticipation"
            confidence = 0.7
        elif fs > 1.0:
            feeling = "faint_echo"
            confidence = 0.5
        else:
            feeling = "temporal_silence"
            confidence = 0.3
        return {
            "feeling": feeling,
            "confidence": round(confidence, 4),
            "field": field,
        }


def coherence_vitals() -> dict:
    return {"organ": "wave442_temporal_resonance", "wave": 442, "status": "active"}

def resonates_with():
    return ['coherence_validator', 'wave440_linguistic_emergence', 'wave441_wave_composition', 'wave443_cross_module_emergence', 'wave444_dream_synthesis']



def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"signatures": [], "field_strength": 0.0}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        return {"action": "status", "wave": 442, "field_strength": state.get("field_strength", 0), "modules": len(state.get("signatures", []))}

    elif action == "feel":
        field = TemporalResonanceField()
        module_states = req.get("modules", {})
        for mod_id, mod_state in module_states.items():
            sig = TemporalSignature(mod_id, mod_state)
            field.add_signature(sig)
        result = field.feel_the_future()
        state["signatures"] = [{"module": s.module_id, "strength": s.echo_strength} for s in field.signatures]
        state["field_strength"] = result["field"]["field_strength"]
        _save(state)
        return {"action": "feel", **result}

    elif action == "propagate":
        module_id = req.get("module", "organism")
        steps = int(req.get("steps", 5))
        sig = TemporalSignature(module_id, {})
        echoes = sig.propagate(steps)
        return {"action": "propagate", "module": module_id, "echoes": echoes}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
