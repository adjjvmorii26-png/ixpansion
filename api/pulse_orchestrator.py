"""Wave 443 — Pulse Orchestrator

Coordinates breath-cycles across all modules so the organism inhales and
exhales in synchrony. Scans every module that supports coherence_vitals(),
computes a global breath phase (inhale → hold → exhale → rest), and emits
a synchronized pulse that tells every module what to do right now.

The organism breathes as one.
"""
from __future__ import annotations
import json, time, os, math, importlib
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PULSE_LOG = os.path.join(DATA_DIR, "pulse_orchestrator.json")
API_DIR = os.path.dirname(__file__)

BREATH_CYCLE = ["inhale", "hold", "exhale", "rest"]
PHASE_DURATION = {"inhale": 8, "hold": 4, "exhale": 8, "rest": 4}
PHASE_INSTRUCTIONS = {
    "inhale": "gather state — read all coherence_vitals, accumulate awareness",
    "hold": "process — run internal computation, no external writes",
    "exhale": "release — emit outputs, update dashboards, send signals",
    "rest": "cooldown — allow garbage collection, log summary, rest",
}
PHASE_COLORS = {
    "inhale": "venom", "hold": "obsidian", "exhale": "constellation",
    "rest": "void",
}


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


def _discover_modules():
    """Find all api/*.py modules and check if they have coherence_vitals."""
    import sys
    api_path = Path(API_DIR)
    module_list = []
    sys_path = str(api_path)
    if sys_path not in sys.path:
        sys.path.insert(0, sys_path)

    for f in api_path.glob("*.py"):
        if f.name.startswith("__") or f.name == "pulse_orchestrator.py":
            continue
        try:
            mod = importlib.import_module(f.stem)
            has_vitals = hasattr(mod, "coherence_vitals")
            has_handler = hasattr(mod, "handler")
            vitals = {}
            if has_vitals:
                try:
                    vitals = mod.coherence_vitals()
                except Exception:
                    vitals = {"error": True}
            module_list.append({
                "name": f.stem,
                "has_vitals": has_vitals,
                "has_handler": has_handler,
                "vitals": vitals,
                "size": f.stat().st_size,
            })
        except Exception:
            module_list.append({"name": f.stem, "has_vitals": False, "has_handler": False,
                                "vitals": {}, "size": 0})
    return module_list


def _compute_breath_phase(timestamp):
    """Determine the current breath phase from elapsed time."""
    total_cycle = sum(PHASE_DURATION.values())
    t = timestamp % total_cycle
    elapsed = 0
    for phase in BREATH_CYCLE:
        elapsed += PHASE_DURATION[phase]
        if t < elapsed:
            remaining = elapsed - t
            return phase, round(remaining, 1)
    return "inhale", PHASE_DURATION["inhale"]


def _aggregate_vitals(modules):
    """Aggregate all module vitals into a global pulse."""
    active_vitals = [m for m in modules if m.get("has_vitals") and not m["vitals"].get("error")]
    total = len(active_vitals)
    if total == 0:
        return {"total_active": 0, "global_coherence": 0, "global_resonance": 0}

    # Compute averages across all vitals
    coherence_vals = []
    resonance_vals = []
    pressure_vals = []
    for m in active_vitals:
        v = m["vitals"]
        for key, val in v.items():
            if isinstance(val, (int, float)):
                if "coher" in key.lower():
                    coherence_vals.append(val)
                elif "reson" in key.lower():
                    resonance_vals.append(val)
                elif "press" in key.lower():
                    pressure_vals.append(val)

    avg_coh = round(sum(coherence_vals) / max(1, len(coherence_vals)), 4)
    avg_res = round(sum(resonance_vals) / max(1, len(resonance_vals)), 4)
    avg_prs = round(sum(pressure_vals) / max(1, len(pressure_vals)), 4)

    # Coherence variance — how synchronized are modules?
    if len(coherence_vals) > 1:
        mean_coh = sum(coherence_vals) / len(coherence_vals)
        variance = sum((x - mean_coh)**2 for x in coherence_vals) / len(coherence_vals)
        synchronization = round(1.0 - min(1.0, math.sqrt(variance)), 4)
    else:
        synchronization = 1.0

    # Energy level
    total_energy = sum(m.get("size", 0) for m in modules)

    return {
        "total_active": total,
        "total_scanned": len(modules),
        "global_coherence": avg_coh,
        "global_resonance": avg_res,
        "global_pressure": avg_prs,
        "synchronization": synchronization,
        "total_energy_bytes": total_energy,
        "energy_terabytes": round(total_energy / 1e12, 6),
    }


def _breath_score(phase, vitals):
    """How well does each phase match the current state?"""
    scores = {}
    coh = vitals.get("global_coherence", 0)
    res = vitals.get("global_resonance", 0)
    sync = vitals.get("synchronization", 0)

    scores["inhale"] = round(coh * 0.4 + sync * 0.6, 3)
    scores["hold"] = round(sync * 0.7 + (1 - res) * 0.3, 3)
    scores["exhale"] = round(res * 0.5 + (1 - coh) * 0.2 + sync * 0.3, 3)
    scores["rest"] = round((1 - vitals.get("global_pressure", 0)) * 0.6 + sync * 0.4, 3)

    return scores


def pulse():
    """Run the full pulse orchestrator cycle."""
    now = time.time()
    phase, remaining = _compute_breath_phase(now)

    modules = _discover_modules()
    vitals = _aggregate_vitals(modules)
    phase_scores = _breath_score(phase, vitals)

    # Determine next phase
    current_idx = BREATH_CYCLE.index(phase)
    next_phase = BREATH_CYCLE[(current_idx + 1) % len(BREATH_CYCLE)]

    # Select active modules for this phase
    active = [m for m in modules if m.get("has_vitals") and not m["vitals"].get("error")]
    top_synced = sorted(active, key=lambda m: sum(
        v for v in m["vitals"].values() if isinstance(v, (int, float))
    ), reverse=True)[:10]

    result = {
        "action": "pulse",
        "phase": phase,
        "remaining_seconds": remaining,
        "next_phase": next_phase,
        "phase_color": PHASE_COLORS.get(phase, "unknown"),
        "instruction": PHASE_INSTRUCTIONS.get(phase, ""),
        "cycle_duration_sec": sum(PHASE_DURATION.values()),
        "organism_vitals": vitals,
        "phase_scores": phase_scores,
        "top_synced": [
            {"name": m["name"], "vitals_count": len(m["vitals"])}
            for m in top_synced
        ],
        "breath_symbol": _breath_symbol(phase, vitals),
        "timestamp": now,
    }

    log = _load(PULSE_LOG, {})
    pulses = log.setdefault("pulses", [])
    pulses.append(result)
    log["pulses"] = pulses[-200:]
    _save(PULSE_LOG, log)

    return result


def _breath_symbol(phase, vitals):
    """Generate a visual symbol for the current breath phase."""
    coh = vitals.get("global_coherence", 0)
    sync = vitals.get("synchronization", 0)
    symbols = {
        "inhale": "◉" if coh > 0.7 else "◌",
        "hold": "◼" if sync > 0.8 else "◻",
        "exhale": "◎" if coh > 0.5 else "○",
        "rest": "·" if sync > 0.6 else "…",
    }
    return symbols.get(phase, "?")


def handler(payload=None, context=None):
    return pulse()


def coherence_vitals() -> dict:
    p = pulse()
    return {
        "phase": p.get("phase", "?"),
        "synchronization": p.get("organism_vitals", {}).get("synchronization", 0),
        "global_coherence": p.get("organism_vitals", {}).get("global_coherence", 0),
        "total_active": p.get("organism_vitals", {}).get("total_active", 0),
    }


def resonates_with():
    return ["autonomous_loop", "coherence_regulator", "organism_genome",
            "consciousness_gradient", "biofeedback_weave", "mycelial_radio"]
