"""Wave 637 — Meta-Regulation Engine.

Expands adaptive regulation with meta-level control:
- Mode scheduling & prediction (anticipate transitions)
- Regulatory memory (learn from past cycles)
- Cross-mode interference detection
- Homeostatic setpoint adjustment
- Regulatory genome (evolvable policy DNA)
"""
import json, time
from pathlib import Path

STATE = Path("data/wave637_meta_regulation.json")

def _load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {
        "current_mode": "healing",
        "mode_history": [],
        "predicted_mode": "healing",
        "prediction_confidence": 0.0,
        "setpoints": {"exploration": 0.75, "healing": 0.4, "mutation": 0.6},
        "genome": {"adaptability": 0.5, "stability": 0.5, "exploration_bias": 0.0},
        "regulation_cycles": 0,
        "tick": 0,
        "interference_log": [],
        "homeostatic_memory": [],
    }

def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))

def _now():
    return time.time()

MODES = {
    "exploration": {"desc": "High coherence — modules roam freely", "energy": "high", "mutation": False, "connections": True},
    "healing": {"desc": "Low coherence — conserve energy, stabilize", "energy": "conserving", "mutation": False, "connections": False},
    "mutation": {"desc": "Divergent coherence — structural change", "energy": "chaotic", "mutation": True, "connections": True},
    "consolidation": {"desc": "Post-mutation stabilization", "energy": "moderate", "mutation": False, "connections": False},
    "dreaming": {"desc": "Low activity — subconscious processing", "energy": "low", "mutation": False, "connections": False},
}

def _evaluate(avg_coherence, variance, genome=None):
    """Determine mode with genome-influenced thresholds."""
    g = genome or {"adaptability": 0.5, "exploration_bias": 0.0}
    adapt = g.get("adaptability", 0.5)
    bias = g.get("exploration_bias", 0.0)
    
    # Genome shifts thresholds
    exp_thresh = 0.75 - (adapt * 0.1) + (bias * 0.1)
    heal_thresh = 0.4 + (adapt * 0.05)
    mut_thresh = 0.6 - (adapt * 0.1)
    
    if avg_coherence >= exp_thresh and variance < 0.1:
        return "exploration"
    if avg_coherence < heal_thresh:
        return "healing"
    if variance > 0.25:
        return "mutation"
    if avg_coherence > 0.6 and variance < 0.05:
        return "consolidation"
    return "healing"

def _predict_next(history, current_mode, genome):
    """Predict next mode based on history patterns."""
    if len(history) < 3:
        return current_mode, 0.3
    
    # Simple Markov: look at transitions from current mode
    transitions = {}
    for i in range(len(history) - 1):
        if history[i]["to"] == current_mode:
            nxt = history[i + 1]["to"]
            transitions[nxt] = transitions.get(nxt, 0) + 1
    
    if transitions:
        predicted = max(transitions, key=transitions.get)
        conf = transitions[predicted] / sum(transitions.values())
        # Genome adaptability increases confidence
        conf = min(0.95, conf + g.get("adaptability", 0.5) * 0.2)
        return predicted, round(conf, 3)
    return current_mode, 0.3

def _detect_interference(mode_history):
    """Detect cross-mode interference patterns."""
    if len(mode_history) < 5:
        return []
    
    interferences = []
    recent = mode_history[-5:]
    
    # Rapid oscillation = interference
    modes = [h["to"] for h in recent]
    for i in range(1, len(modes)):
        if modes[i] != modes[i-1]:
            # Check for A->B->A pattern
            if i >= 2 and modes[i] == modes[i-2]:
                interferences.append({
                    "type": "oscillation",
                    "pattern": "->".join(modes[i-2:i+1]),
                    "severity": "high"
                })
    
    # Stuck in one mode too long
    if len(set(modes)) == 1 and len(modes) >= 5:
        interferences.append({
            "type": "stagnation",
            "mode": modes[0],
            "duration": len(modes),
            "severity": "medium"
        })
    
    return interferences

def _adjust_setpoints(genome, performance):
    """Evolve homeostatic setpoints based on performance."""
    new_setpoints = {}
    for mode, sp in genome.get("setpoints", {}).items():
        # Slight random drift toward better performance
        drift = (performance.get(mode, 0.5) - 0.5) * 0.02
        new_setpoints[mode] = round(max(0.1, min(0.9, sp + drift)), 3)
    return new_setpoints

def _mutate_genome(genome, mutation_rate=0.05):
    """Evolve the regulatory genome."""
    import random
    new_genome = genome.copy()
    for key in ["adaptability", "stability", "exploration_bias"]:
        if random.random() < mutation_rate:
            current = new_genome.get(key, 0.5)
            delta = random.uniform(-0.1, 0.1)
            new_genome[key] = round(max(0.0, min(1.0, current + delta)), 3)
    return new_genome

def _assess(coherence_data):
    """Run meta-regulatory cycle."""
    s = _load()
    s["regulation_cycles"] += 1
    s["tick"] += 1

    modules = coherence_data.get("modules", {})
    if not modules:
        avg_coherence = coherence_data.get("avg_coherence", 0.5)
        variance = coherence_data.get("variance", 0.0)
    else:
        values = list(modules.values())
        avg_coherence = sum(values) / len(values)
        variance = sum((v - avg_coherence) ** 2 for v in values) / len(values)

    genome = s.get("genome", {"adaptability": 0.5, "stability": 0.5, "exploration_bias": 0.0})
    new_mode = _evaluate(avg_coherence, variance, genome)
    old_mode = s["current_mode"]

    s["current_mode"] = new_mode
    s["mode_history"].append({
        "cycle": s["regulation_cycles"],
        "from": old_mode,
        "to": new_mode,
        "avg_coherence": round(avg_coherence, 4),
        "variance": round(variance, 4),
        "time": _now(),
    })
    s["mode_history"] = s["mode_history"][-200:]

    # Prediction
    s["predicted_mode"], s["prediction_confidence"] = _predict_next(
        s["mode_history"], new_mode, genome
    )

    # Interference detection
    interference = _detect_interference(s["mode_history"])
    if interference:
        s["interference_log"].extend(interference)
        s["interference_log"] = s["interference_log"][-50:]

    # Homeostatic memory
    s["homeostatic_memory"].append({
        "cycle": s["regulation_cycles"],
        "mode": new_mode,
        "coherence": round(avg_coherence, 4),
        "variance": round(variance, 4),
        "setpoints": s["setpoints"].copy(),
    })
    s["homeostatic_memory"] = s["homeostatic_memory"][-100:]

    # Evolve genome every 10 cycles
    if s["regulation_cycles"] % 10 == 0:
        s["genome"] = _mutate_genome(genome)
        s["setpoints"] = _adjust_setpoints(genome, _calculate_performance(s["homeostatic_memory"]))

    _save(s)

    return {
        "cycle": s["regulation_cycles"],
        "mode": new_mode,
        "mode_info": MODES.get(new_mode, {}),
        "avg_coherence": round(avg_coherence, 4),
        "variance": round(variance, 4),
        "mode_changed": old_mode != new_mode,
        "predicted_next": s["predicted_mode"],
        "prediction_confidence": s["prediction_confidence"],
        "genome": s["genome"],
        "interferences": interference,
    }

def _calculate_performance(memory):
    """Calculate performance per mode from memory."""
    perf = {}
    for mode in MODES:
        mode_cycles = [m for m in memory if m["mode"] == mode]
        if mode_cycles:
            perf[mode] = sum(m["coherence"] for m in mode_cycles) / len(mode_cycles)
        else:
            perf[mode] = 0.5
    return perf

def _status():
    s = _load()
    return {
        "tick": s["tick"],
        "current_mode": s["current_mode"],
        "cycles": s["regulation_cycles"],
        "genome": s.get("genome", {}),
        "setpoints": s.get("setpoints", {}),
        "predicted_mode": s.get("predicted_mode", "healing"),
        "prediction_confidence": s.get("prediction_confidence", 0.0),
        "interferences": s.get("interference_log", [])[-3:],
        "recent_transitions": s["mode_history"][-3:],
    }

def _genome_status():
    s = _load()
    return {"genome": s.get("genome", {}), "setpoints": s.get("setpoints", {})}

def handler(req):
    action = req.get("action", "status")
    if action == "status":
        return {"ok": True, **_status()}
    elif action == "assess":
        return {"ok": True, **_assess(req.get("coherence", {}))}
    elif action == "genome":
        return {"ok": True, **_genome_status()}
    elif action == "predict":
        s = _load()
        pred, conf = _predict_next(s["mode_history"], s["current_mode"], s.get("genome", {}))
        return {"ok": True, "predicted": pred, "confidence": conf}
    elif action == "interference":
        s = _load()
        return {"ok": True, "interferences": s.get("interference_log", [])}
    elif action == "mutate_genome":
        s = _load()
        s["genome"] = _mutate_genome(s.get("genome", {}), req.get("rate", 0.05))
        _save(s)
        return {"ok": True, "genome": s["genome"]}
    return {"ok": False, "error": f"Unknown action: {action}"}

def coherence_vitals():
    s = _load()
    return {"wave": 637, "mode": s["current_mode"], "cycles": s["regulation_cycles"], "genome": s.get("genome", {})}

def resonates_with():
    return ["wave636_adaptive_regulation", "wave635_coherence_gradient", "wave634_temporal_field", "wave626_dream_synthesis"]
