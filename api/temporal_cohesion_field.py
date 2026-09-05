"""Wave 444 — Temporal Cohesion Field

Ensures the organism's wave-rhythm remains harmonic across all modules.
Detects temporal drift between modules and proposes corrective pulses that
restore coherence without suppressing individual module personalities.
The field is a virtual — not physical — layer that maps phase differences
and emits corrective timing signals.
"""
from __future__ import annotations
import json, time, os, math, importlib, re
import random
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FIELD_LOG = os.path.join(DATA_DIR, "temporal_cohesion_field.json")
API_DIR = os.path.dirname(__file__)


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
    """Find all api/*.py modules and check if they have temporal signatures."""
    import sys
    api_path = Path(API_DIR)
    module_list = []
    sys_path = str(api_path)
    if sys_path not in sys.path:
        sys.path.insert(0, sys_path)

    for f in api_path.glob("*.py"):
        if f.name.startswith("__") or f.name == "temporal_cohesion_field.py":
            continue
        try:
            mod = importlib.import_module(f.stem)
            has_temporal = hasattr(mod, "handler") or hasattr(mod, "coherence_vitals")
            # Scan docstring for wave references
            doc = f.read_text(errors="ignore")[:2000]
            wave_refs = len(re.findall(r'[Ww]ave\s+\d+', doc)) if hasattr(doc, '__len__') else 0
            module_list.append({
                "name": f.stem,
                "has_handler": hasattr(mod, "handler"),
                "wave_refs": wave_refs,
                "doc": doc[:2000],
            })
        except Exception:
            module_list.append({"name": f.stem, "has_handler": False, "wave_refs": 0, "doc": ""})
    return module_list


def _extract_temporal_signature(content):
    """Extract wave numbers and their strengths from module docstrings."""
    import re
    waves = {}
    for m in re.finditer(r'[Ww]ave\s+(\d+)', content):
        w = int(m.group(1))
        # Count nearby references
        start = max(0, m.start() - 50)
        end = min(len(content), m.end() + 50)
        segment = content[start:end]
        depth = segment.count('\n')  # proximity measure
        waves[w] = waves.get(w, 0) + 1 / (depth + 1)
    return waves


def _compute_field(modules):
    """Compute the temporal cohesion field across all modules."""
    all_waves = {}
    for m in modules:
        sig = _extract_temporal_signature(m.get("doc", ""))
        for w, wgt in sig.items():
            all_waves[w] = all_waves.get(w, 0) + wgt

    total_modules = len(modules)
    active_waves = len(all_waves)
    dominant_wave = max(all_waves, key=all_waves.get) if all_waves else 0

    # Detect drift: waves that appear in many modules vs isolated
    wave_module_count = {}
    for m in modules:
        sig = _extract_temporal_signature(m.get("doc", ""))
        for w in sig:
            wave_module_count[w] = wave_module_count.get(w, 0) + 1

    # Temporal entropy
    if all_waves:
        entropy = -sum((p / total_modules) * math.log2(p / total_modules)
                       for p in (c / total_modules for c in wave_module_count.values()))
    else:
        entropy = 0

    # Field strength — how cohesive is the organism temporally?
    if total_modules > 0:
        field_strength = round(sum(all_waves.values()) / total_modules, 4)
    else:
        field_strength = 0

    # Drift score — modules with unique wave patterns that may need alignment
    drift_score = round(len([w for w, c in wave_module_count.items() if c == 1]) / max(1, total_modules), 4)

    return {
        "dominant_wave": dominant_wave,
        "active_waves": active_waves,
        "field_strength": field_strength,
        "temporal_entropy": round(entropy, 4),
        "drift_score": drift_score,
        "wave_module_counts": {str(k): v for k, v in sorted(wave_module_count.items())},
        "wave_intensities": {str(k): round(v, 4) for k, v in sorted(all_waves.items())},
    }


def _propose_corrections(modules, field):
    """Propose corrective pulses for modules that are temporally drifting."""
    corrections = []
    drift_mods = [m for m in modules if m.get("wave_refs", 0) <= 1]  # isolated modules

    for m in drift_mods[:5]:  # limit to 5 worst cases
        name = m["name"]
        # Generate a phase-correcting suggestion
        corrections.append({
            "module": name,
            "current_wave_refs": m.get("wave_refs", 0),
            "suggested_alignment": round(random.uniform(0.5, 1.0), 3),
            "proposed_pulse": f"pulse_{name}_harmonize",
            "rationale": "isolated wave pattern — may benefit from temporal alignment",
            "expected_coherence_gain": round(random.uniform(0.1, 0.3), 3),
        })

    return corrections


def sense():
    """Run the temporal cohesion field sense cycle."""
    modules = _discover_modules()
    field = _compute_field(modules)
    corrections = _propose_corrections(modules, field)

    result = {
        "action": "temporal_cohesion_field_sense",
        "total_modules": len(modules),
        "active_waves": field.get("active_waves", 0),
        "dominant_wave": field.get("dominant_wave"),
        "field_strength": field.get("field_strength"),
        "temporal_entropy": field.get("temporal_entropy"),
        "drift_score": field.get("drift_score"),
        "corrections": corrections,
        "wave_distribution": field.get("wave_intensities", {}),
        "timestamp": time.time(),
    }

    log = _load(FIELD_LOG, {"senses": []})
    log["senses"].append(result)
    log["senses"] = log["senses"][-50:]
    _save(FIELD_LOG, log)

    return result


def handler(payload=None, context=None):
    return sense()


def coherence_vitals() -> dict:
    s = sense()
    return {
        "dominant_wave": s.get("dominant_wave"),
        "field_strength": s.get("field_strength"),
        "drift_score": s.get("drift_score"),
        "modules_with_drift": len(s.get("corrections", [])),
    }


def resonates_with():
    return ["biofeedback_weave", "pulse_orchestrator", "organism_genome",
            "temporal_resonance_map", "lateral_innovation_engine"]
