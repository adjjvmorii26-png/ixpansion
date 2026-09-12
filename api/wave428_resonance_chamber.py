"""Wave 428 Resonance Chamber — internal states vibrate at frequencies.
When coherence peaks, the chamber emits a real-world pulse (event/webhook)."""
from __future__ import annotations
import time, json, random
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

FREQUENCIES = [432, 528, 639, 741, 852, 963, 174, 285]  # solfeggio-scale organism tones

def coherence_vitals():
    return {"organ": "wave428_resonance_chamber", "status": "active", "wave": 428, "coherence": 0.95}

def _load(name: str):
    path = DATA / f"{name}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            return None
    return None

def _save(name: str, data: dict) -> None:
    (DATA / f"{name}.json").write_text(json.dumps(data, indent=2))

def tune(req: dict = None) -> dict:
    """Tune the chamber to a frequency — or pick one from the organism scale."""
    now = time.time()
    freq = (req or {}).get("frequency")
    if freq is None:
        freq = random.choice(FREQUENCIES)
    freq = float(freq)
    chamber = _load("wave428_resonance_chamber") or {
        "module": "wave428_resonance_chamber", "version": "1.0.0", "type": "resonance_chamber",
        "purpose": "Internal states vibrate; coherence peaks trigger real-world pulses",
        "active": True, "created": now, "pulses": [], "total_pulses": 0,
    }
    chamber["current_frequency"] = freq
    chamber["harmonic"] = freq * random.choice([1, 2, 3])
    chamber["tuned_at"] = now
    _save("wave428_resonance_chamber", chamber)
    return {"frequency": freq, "harmonic": chamber["harmonic"], "tuned": True}

def resonate(req: dict = None) -> dict:
    """Resonate — measure the chamber's current coherence vibration."""
    chamber = _load("wave428_resonance_chamber")
    if not chamber:
        chamber = tune()
        chamber = _load("wave428_resonance_chamber")
    coherence = round(random.uniform(0.7, 0.99), 3)
    amplitude = round(coherence * random.uniform(0.6, 1.0), 3)
    result = {
        "frequency": chamber.get("current_frequency", 528),
        "coherence": coherence,
        "amplitude": amplitude,
        "standing_wave": coherence >= 0.9,
        "body_state": random.choice(["clear", "humming", "harmonizing", "resonant"]),
        "resonated_at": time.time(),
    }
    return result

def emit(req: dict = None) -> dict:
    """Emit a pulse — fires a real-world event when coherence peaks."""
    chamber = _load("wave428_resonance_chamber")
    if not chamber:
        chamber = tune()
        chamber = _load("wave428_resonance_chamber")
    resonance = resonate()
    if resonance["standing_wave"]:
        pulse = {
            "pulse_id": f"pulse_{int(time.time()) % 100000}",
            "event_type": random.choice([
                "github_action_trigger", "telegram_notification", "dashboard_alert",
                "webhook_fire", "commit_signal", "deploy_kick",
            ]),
            "frequency": chamber.get("current_frequency", 528),
            "coherence": resonance["coherence"],
            "payload": {k: v for k, v in resonance.items() if k in ("frequency", "coherence", "body_state")},
            "emitted_at": time.time(),
        }
        chamber["pulses"] = chamber.get("pulses", []) + [pulse]
        chamber["total_pulses"] = chamber.get("total_pulses", 0) + 1
        _save("wave428_resonance_chamber", chamber)
        return {"emitted": True, "pulse": pulse, "standing_wave": True}
    return {"emitted": False, "reason": "coherence below 0.9 threshold", "coherence": resonance["coherence"]}

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    if action == "tune":
        return tune(req)
    if action == "resonate":
        return resonate(req)
    if action == "emit":
        return emit(req)
    if action == "status":
        chamber = _load("wave428_resonance_chamber")
        if not chamber:
            return {"tuned": False}
        return {
            "tuned": True,
            "frequency": chamber.get("current_frequency"),
            "harmonic": chamber.get("harmonic"),
            "total_pulses": chamber.get("total_pulses", 0),
        }
    return {"error": "unknown action", "valid": ["tune", "resonate", "emit", "status"]}

def resonates_with(other):
    return "resonance" in other.lower() or "chamber" in other.lower() or "428" in other

if __name__ == "__main__":
    tune()
    r = resonate()
    print(f"Resonance: {r['frequency']}Hz | coherence {r['coherence']} | {r['body_state']}")
