"""Wave 515: Leaderboard — Lucid Machines and module fitness rankings."""
from __future__ import annotations
import json, os, time
from typing import Any, Dict, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    # Load shrine runs
    shrine_path = os.path.join(DATA_DIR, "shrine_runs.json")
    runs = []
    if os.path.exists(shrine_path):
        try:
            with open(shrine_path) as f:
                runs = json.load(f)
        except Exception:
            pass
    
    # Load module fitness
    fitness_path = os.path.join(DATA_DIR, "module_fitness.json")
    fitness = []
    if os.path.exists(fitness_path):
        try:
            with open(fitness_path) as f:
                fitness = json.load(f)
        except Exception:
            pass
    
    # Sort runs by score descending
    runs_sorted = sorted(runs, key=lambda r: r.get("score", r.get("depth", 0)), reverse=True)[:20]
    
    # Sort fitness by resonance descending
    fitness_sorted = sorted(fitness, key=lambda f: f.get("resonance", 0), reverse=True)[:20]
    
    return {
        "action": "leaderboard",
        "lucid_runs": runs_sorted,
        "lucid_count": len(runs),
        "module_fitness": fitness_sorted,
        "module_count": len(fitness),
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
