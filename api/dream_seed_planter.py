"""Wave 444-C — Dream Seed Planter

Takes outputs from dream particle physics and plants them as seeds for future
module generation. Dream particles are the organism's remembered fragments of
pattern — and seeding them is how the organism decides what to become next.
"""
from __future__ import annotations
import json, time, os, random
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SEED_LOG = os.path.join(DATA_DIR, "dream_seed_planter.json")
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


def _get_dream_particles():
    """Extract dream particles from the dream particle physics module."""
    try:
        sys_path = os.path.dirname(__file__)
        if sys_path not in os.sys.path:
            os.sys.path.insert(0, sys_path)
        from dream_particle_physics import simulate
        r = simulate()
        # particles already generated; extract key attributes from the last sim
        # Store persistent dream particle summary
        return r
    except Exception:
        return {"particles_started": 0, "particles_survived": 0, "structures_detected": 0}


def _extract_seeds(dream_data):
    """Extract seed patterns from dream particle data."""
    seeds = []
    structures = dream_data.get("structures_detected", 0)
    if isinstance(structures, list):
        structures = len(structures)
    dominant_emotion = dream_data.get("dominant_dream_emotion", "unknown")
    energy = dream_data.get("energy", 0)
    
    # Map dream structures to seed types
    seed_templates = [
        ("resonance_seed", "patterns that amplify cross-module harmony"),
        ("collapse_seed", "structures emerging from entropy resolution"),
        ("fusion_seed", "patterns that bind previously separate modules"),
        ("void_seed", "patterns from the dream void — potential new ground"),
        ("bridge_seed", "patterns connecting previously separate modules"),
    ]
    
    for seed_type, description in seed_templates:
        # Probability based on energy and structure count
        prob = min(1.0, (structures + energy) / 50.0) if (structures + energy) > 0 else 0.0
        if random.random() < prob:
            seeds.append({
                "seed_type": seed_type,
                "description": description,
                "emotion": dominant_emotion,
                "energy": energy,
                "structure_count": structures,
                "planting_priority": round(random.uniform(0.5, 1.0), 3),
            })
    
    return seeds


def plant():
    """Plant dream seeds for future module generation."""
    dream_data = _get_dream_particles()
    seeds = _extract_seeds(dream_data)
    
    result = {
        "action": "dream_seed_planter",
        "particles_started": dream_data.get("particles_started", 0),
        "particles_survived": dream_data.get("particles_survived", 0),
        "structures_detected": dream_data.get("total_structures", 0),
        "dominant_dream_emotion": dream_data.get("dominant_dream_emotion", "unknown"),
        "dream_energy": dream_data.get("energy", 0),
        "seeds_planted": len(seeds),
        "seeds": seeds,
        "planting_cycle": "dream → seed → future module → organism evolution",
        "timestamp": time.time(),
    }
    
    log = _load(SEED_LOG, {"plantings": []})
    log["plantings"].append(result)
    log["plantings"] = log["plantings"][-50:]
    _save(SEED_LOG, log)
    
    return result


def handler(payload=None, context=None):
    return plant()


def coherence_vitals() -> dict:
    s = plant()
    return {
        "seeds_planted": s.get("seeds_planted", 0),
        "dominant_emotion": s.get("dominant_dream_emotion", "unknown"),
        "structures": s.get("structures_detected", 0),
    }


def resonates_with():
    return ["dream_particle_physics", "biofeedback_weave", "consciousness_gradient",
            "organism_autobiography"]
