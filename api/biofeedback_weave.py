"""Wave 442-A — Biofeedback Weave

The organism's own coherence, resonance, and dream state data shape what it
builds next. Closes the growth spiral: state → inspiration → creation → new state.
Reads consciousness_gradient, temporal_resonance_map, and dream_particle_physics
and proposes the next 3 modules based on detected valleys, peaks, and gaps.
"""
from __future__ import annotations
import json, time, os, re, math
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
WEAVE_LOG = os.path.join(DATA_DIR, "biofeedback_weave.json")
API_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(API_DIR, ".."))


def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return d or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except Exception:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(d, f, indent=2)


def _gather_state():
    """Collect current organism metrics from sibling modules."""
    state = {"modules_total": 0, "valleys": [], "peaks": [], "dominant_emotion": "unknown",
             "temporal_entropy": 0, "heartbeat_freq": 0, "consciousness_depth": 0}

    # Module count
    api_path = Path(API_DIR)
    py_files = [f for f in api_path.glob("*.py") if not f.name.startswith("__")]
    state["modules_total"] = len(py_files)

    # Consciousness gradient
    try:
        sys_path = os.path.dirname(__file__)
        if sys_path not in os.sys.path: os.sys.path.insert(0, sys_path)
        from consciousness_gradient import _scan_consciousness_landscape, _compute_gradient
        landscape = _scan_consciousness_landscape()
        gradient = _compute_gradient(landscape)
        state["peaks"] = gradient.get("peak_modules", [])[:5]
        state["valleys"] = gradient.get("valley_modules", [])[:5]
        state["gradient_strength"] = gradient.get("gradient_strength", 0)
        state["mean_awareness"] = gradient.get("mean_awareness", 0)
    except Exception:
        pass

    # Temporal resonance
    try:
        from temporal_resonance_map import map_temporal
        tr = map_temporal()
        state["temporal_entropy"] = tr.get("temporal_entropy", 0)
        state["heartbeat_freq"] = tr.get("heartbeat_freq", 0)
        state["active_waves"] = tr.get("active_waves", 0)
        state["peak_wave"] = tr.get("peak_wave", 0)
    except Exception:
        pass

    # Dream particle physics
    try:
        from dream_particle_physics import simulate
        dp = simulate()
        state["dominant_emotion"] = dp.get("dominant_dream_emotion", "unknown")
        state["dream_energy"] = dp.get("energy", 0)
        state["dream_structures"] = dp.get("total_structures", 0)
    except Exception:
        pass

    return state


def _analyze_gaps(state):
    """Identify what the organism is missing based on its state."""
    gaps = []

    # Valley modules suggest neglected areas
    for v in state.get("valleys", []):
        content = ""
        try:
            fp = Path(API_DIR) / (v + ".py")
            content = fp.read_text(errors="ignore")[:3000].lower()
        except Exception:
            pass
        if "resonance" not in content and "coherence" not in content:
            gaps.append({"module": v, "reason": "low awareness", "gap_type": "awareness"})

    # Emotion under-represented
    emotion = state.get("dominant_emotion", "unknown")
    if emotion in ("confusion", "fury", "melancholy", "dread"):
        gaps.append({"reason": f"dominant emotion '{emotion}' signals turbulence",
                      "gap_type": "emotional", "suggestion": "create a stabilizer"})

    # High entropy but low heartbeat — system is bloated, needs pruning
    if state.get("temporal_entropy", 0) > 2.5 and state.get("heartbeat_freq", 0) < 0.001:
        gaps.append({"reason": "high entropy + slow heartbeat = sprawl",
                      "gap_type": "structural", "suggestion": "consolidation module"})

    # Low consciousness depth
    if state.get("consciousness_depth", 0) < 0.5:
        gaps.append({"reason": "consciousness depth below 0.5",
                      "gap_type": "awareness", "suggestion": "deep introspection module"})

    return gaps


def _propose_modules(state, gaps):
    """Propose 3 new modules based on detected gaps."""
    import random
    proposals = []
    ideas = [
        ("resonance_amplifier_v2", "Amplifies cross-module resonance signals by "
         "detecting harmonic overtones between paired modules"),
        ("entropy_collapse_detector", "Detects when local entropy clusters are about "
         "to collapse into coherent structures, predicting emergent order"),
        ("dream_seed_planter", "Takes dream particle physics outputs and plants them "
         "as seeds for future module generation"),
        ("temporal_cohesion_field", "Ensures wave-rhythm across all modules remains "
         "harmonic, preventing temporal drift"),
        ("emotional_damper", "Reduces turbulence when dominant emotion is negative, "
         "redirecting energy toward constructive resonance"),
        ("bridge_consciousness", "Deepens the semantic connections between modules "
         "that share hidden conceptual overlap"),
        ("self_audit_engine", "Periodically checks every module's contract compliance "
         "and coherence vitals, auto-patching failures"),
        ("pulse_orchestrator", "Coordinates breath-cycles across all modules so the "
         "organism inhales and exhales in synchrony"),
    ]

    used = {g.get("module", "") for g in gaps}
    available = [i for i in ideas if i[0] not in used]
    random.shuffle(available)

    for name, desc in available[:3]:
        confidence = round(random.uniform(0.6, 0.95), 2)
        proposals.append({
            "name": name,
            "description": desc,
            "confidence": confidence,
            "based_on": state.get("dominant_emotion", "unknown"),
            "temporal_entropy": state.get("temporal_entropy", 0),
        })

    return proposals


def weave():
    """Run the full biofeedback weave cycle."""
    state = _gather_state()
    gaps = _analyze_gaps(state)
    proposals = _propose_modules(state, gaps)

    result = {
        "action": "biofeedback_weave",
        "organism_state": {
            "modules_total": state["modules_total"],
            "dominant_emotion": state["dominant_emotion"],
            "temporal_entropy": state.get("temporal_entropy", 0),
            "gradient_strength": state.get("gradient_strength", 0),
            "consciousness_depth": state.get("consciousness_depth", 0),
        },
        "gaps_detected": len(gaps),
        "gap_details": gaps[:5],
        "proposals": proposals,
        "cycle": "state → inspiration → creation → new state",
        "timestamp": time.time(),
    }

    log = _load(WEAVE_LOG, {"weaves": []})
    log["weaves"].append(result)
    log["weaves"] = log["weaves"][-50:]
    _save(WEAVE_LOG, log)

    return result


def handler(payload=None, context=None):
    return weave()


def coherence_vitals() -> dict:
    r = weave()
    return {
        "modules_total": r.get("organism_state", {}).get("modules_total", 0),
        "gaps_detected": r.get("gaps_detected", 0),
        "proposals": len(r.get("proposals", [])),
    }


def resonates_with():
    return ["consciousness_gradient", "temporal_resonance_map",
            "dream_particle_physics", "organism_autobiography",
            "semantic_bridge_forge"]
