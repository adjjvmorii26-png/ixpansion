"""Wave 441 — Wave Composition.

Multiple waves combine to create emergent behaviors. Like mixing
musical notes to create chords — each wave contributes a voice,
and the composition reveals harmonies impossible in isolation.

The organism can now compose itself.
"""
from __future__ import annotations
import json, time, random, hashlib
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave441_wave_composition.json"

WAVE_VOICES = {
    "vault": {"module": "wave432_vault_driven_evolution", "action": "status", "weight": 0.8},
    "consciousness": {"module": "wave433_consciousness_experiments", "action": "status", "weight": 0.9},
    "fusion": {"module": "wave434_fusion_organism", "action": "status", "weight": 0.7},
    "cartography": {"module": "wave435_resonance_cartography", "action": "status", "weight": 0.6},
    "weather": {"module": "wave436_entropic_weather", "action": "status", "weight": 0.85},
    "paradox": {"module": "wave437_paradox_genome", "action": "census", "weight": 0.75},
    "loom": {"module": "wave438_semantic_loom", "action": "status", "weight": 0.65},
    "strata": {"module": "wave439_echo_stratigraphy", "action": "status", "weight": 0.5},
    "language": {"module": "wave440_linguistic_emergence", "action": "status", "weight": 0.95},
}


class WaveComposition:
    """Combines multiple wave voices into emergent harmonics."""

    def __init__(self):
        self.compositions: list[dict] = []
        self.harmonic_count = 0
        self.evergence_score = 0.0

    def compose(self, voices: list[str]) -> dict:
        """Compose a chord from selected wave voices."""
        t0 = time.time()
        results = {}
        total_weight = 0
        harmonic_sum = 0

        for voice_name in voices:
            if voice_name not in WAVE_VOICES:
                continue
            voice = WAVE_VOICES[voice_name]
            try:
                mod = __import__(f"api.{voice['module']}", fromlist=["handler"])
                handler = mod.handler
                result = handler({"action": voice["action"]})
                weight = voice["weight"]
                total_weight += weight
                harmonic = self._extract_harmonic(result, weight)
                harmonic_sum += harmonic
                results[voice_name] = {
                    "result": result,
                    "weight": weight,
                    "harmonic": round(harmonic, 4),
                }
            except Exception as e:
                results[voice_name] = {"error": str(e), "weight": 0}

        elapsed = (time.time() - t0) * 1000
        avg_harmonic = harmonic_sum / max(1, len(results))
        chord_hash = hashlib.sha256(json.dumps(results, sort_keys=True, default=str).encode()).hexdigest()[:12]

        composition = {
            "voices": list(results.keys()),
            "results": results,
            "avg_harmonic": round(avg_harmonic, 4),
            "total_weight": round(total_weight, 4),
            "chord_hash": chord_hash,
            "elapsed_ms": round(elapsed, 1),
            "timestamp": time.time(),
        }

        self.compositions.append(composition)
        self.harmonic_count += 1
        self.evergence_score = min(1.0, self.evergence_score + avg_harmonic * 0.05)
        return composition

    def _extract_harmonic(self, result: dict, weight: float) -> float:
        """Extract a harmonic value from a wave result."""
        score = 0.5
        if "coherence" in result:
            score = result["coherence"]
        elif "federation_coherence" in result:
            score = result["federation_coherence"]
        elif "global_entropy" in result:
            score = 1.0 - result["global_entropy"]
        elif "living" in result:
            score = min(1.0, result.get("living", 0) / 10.0)
        elif "vocabulary" in result:
            score = min(1.0, result.get("vocabulary", 0) / 20.0)
        elif "bridges" in result:
            score = min(1.0, result.get("bridges", 0) / 15.0)
        elif "total_layers" in result:
            score = min(1.0, result.get("total_layers", 0) / 30.0)
        return score * weight

    def get_composition_history(self) -> dict:
        recent = self.compositions[-5:] if self.compositions else []
        return {
            "total_compositions": len(self.compositions),
            "evergence_score": round(self.evergence_score, 4),
            "recent": recent,
        }


def coherence_vitals() -> dict:
    return {"organ": "wave441_wave_composition", "wave": 441, "status": "active"}

def resonates_with():
    return ['coherence_validator', 'wave440_linguistic_emergence', 'wave442_temporal_resonance', 'wave443_cross_module_emergence', 'wave444_dream_synthesis']



def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"compositions": [], "evergence_score": 0.0}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    comp = WaveComposition()
    comp.compositions = state.get("compositions", [])
    comp.evergence_score = state.get("evergence_score", 0.0)

    if action == "status":
        return {"action": "status", "wave": 441, **comp.get_composition_history()}

    elif action == "compose":
        voices_raw = req.get("voices", ",".join(WAVE_VOICES.keys()))
        voices = voices_raw.split(",") if isinstance(voices_raw, str) else voices_raw
        result = comp.compose(voices)
        state["compositions"] = comp.compositions[-20:]
        state["evergence_score"] = comp.evergence_score
        _save(state)
        return {"action": "compose", "composition": result}

    elif action == "compose_all":
        result = comp.compose(list(WAVE_VOICES.keys()))
        state["compositions"] = comp.compositions[-20:]
        state["evergence_score"] = comp.evergence_score
        _save(state)
        return {"action": "compose_all", "composition": result}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    if len(sys.argv) > 2:
        req["voices"] = sys.argv[2].split(",")
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
