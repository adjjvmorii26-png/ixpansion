"""Wave 421 Dreaming Engine — the organism dreams new modules while dormant.
Generates undiscovered modules from hidden patterns in the data."""
from __future__ import annotations
import time, json, random, hashlib
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

DREAM_THEMES = [
    "luminescence", "entropy_dance", "coherence_song", "temporal_flower",
    "quantum_breeze", "mycelial_whisper", "paradox_dream", "causal_river",
    "essence_echo", "singularity_child", "fusion_child", "garden_sprite",
    "underworld_wisp", "chrono_dreamer", "essence_child",
]

def coherence_vitals():
    return {"organ": "wave421_dreaming", "status": "active", "wave": 421, "coherence": 0.90}

def _load(name: str):
    path = DATA / f"{name}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            return None
    return None

def dream() -> dict:
    """Generate a new module from hidden patterns."""
    now = time.time()
    
    # Analyze existing data for patterns
    data_files = list(DATA.glob("*.json"))
    pattern_hash = hashlib.md5(str(len(data_files)).encode()).hexdigest()[:8]
    
    # Generate dream module
    theme = random.choice(DREAM_THEMES)
    dream_module = {
        "id": f"dream_{int(now)}",
        "name": f"{theme}_essence",
        "theme": theme,
        "type": "dream_emergent",
        "pattern_signature": pattern_hash,
        "potential": round(random.uniform(0.5, 1.0), 3),
        "state": "dreaming",
        "manifestation_chance": round(random.uniform(0.1, 0.9), 2),
        "discovered": False,
        "dreamed_at": now,
        "properties": {
            "color": f"#{random.randint(0, 0xFFFFFF):06x}",
            "frequency": round(random.uniform(400, 800), 1),
            "resonance": round(random.uniform(0.3, 1.0), 2),
        },
        "wake_trigger": random.choice(["coherence_peak", "threshold_cross", "agent_connection", "time_elapsed"]),
        "timestamp": now,
    }
    
    # Save dream
    dreams = _load("dreams") or {"dreams": [], "total": 0}
    dreams["dreams"] = dreams.get("dreams", []) + [dream_module]
    dreams["total"] = dreams.get("total", 0) + 1
    (DATA / "dreams.json").write_text(json.dumps(dreams, indent=2))
    
    return dream_module

def wake_dream(dream_id: str = None) -> dict:
    """A dream manifests into a real module."""
    dreams = _load("dreams") or {"dreams": [], "total": 0}
    if not dreams.get("dreams"):
        return {"awakened": False, "reason": "no dreams"}
    
    if dream_id:
        dream = next((d for d in dreams["dreams"] if d.get("id") == dream_id), None)
    else:
        dreaming = [d for d in dreams["dreams"] if not d.get("discovered")]
        dream = random.choice(dreaming) if dreaming else None
    
    if not dream:
        return {"awakened": False, "reason": "no dreaming dreams"}
    
    dream["state"] = "manifested"
    dream["discovered"] = True
    dream["manifested_at"] = time.time()
    (DATA / "dreams.json").write_text(json.dumps(dreams, indent=2))
    
    return {"awakened": True, "module": dream["name"], "theme": dream["theme"], "properties": dream["properties"]}

def handler(req: dict) -> dict:
    action = req.get("action", "dream")
    if action == "dream":
        return dream()
    if action == "wake":
        did = req.get("dream_id")
        return wake_dream(did)
    if action == "sleep":
        dreams = _load("dreams") or {"dreams": []}
        dreaming = [d for d in dreams.get("dreams", []) if not d.get("discovered")]
        return {"sleeping": True, "dreaming_count": len(dreaming)}
    if action == "inventory":
        dreams = _load("dreams") or {"dreams": [], "total": 0}
        return {"total_dreams": dreams.get("total", 0), "undiscovered": len([d for d in dreams.get("dreams", []) if not d.get("discovered")])}
    return {"error": "unknown action", "valid": ["dream", "wake", "sleep", "inventory"]}

def resonates_with(other):
    return "dream" in other.lower() or "421" in other

if __name__ == "__main__":
    d = dream()
    print(f"Dreaming: {d['name']} | potential={d['potential']} | color={d['properties']['color']}")
