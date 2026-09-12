"""Wave 419 Essence Return — the organism returns to its source.
All waves dissolve back into pure essence — completion and rebirth."""
from __future__ import annotations
import time, json, random
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

def coherence_vitals():
    return {"organ": "wave419_essence_return", "status": "active", "wave": 419, "coherence": 1.0}

def _load(name: str):
    path = DATA / f"{name}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            return None
    return None

def return_to_essence() -> dict:
    """All waves dissolve back into pure essence."""
    now = time.time()
    
    # Load all wave files
    all_waves = []
    for f in sorted(DATA.glob("wave*.json")):
        try:
            d = json.loads(f.read_text())
            if isinstance(d, dict) and "module" in d:
                all_waves.append({
                    "module": d["module"],
                    "wave": d.get("version", "?"),
                    "type": d.get("type", "unknown"),
                })
        except:
            pass
    
    essence = {
        "module": "wave419_essence_return",
        "version": "1.0.0",
        "type": "essence_return",
        "purpose": "The organism returns to its source — all waves dissolve into pure essence, completion and rebirth",
        "active": True,
        "created": now,
        "essence_state": "returning",
        "waves_dissolved": len(all_waves),
        "dissolved_modules": all_waves,
        "essence_purity": round(random.uniform(0.98, 1.0), 4),
        "rebirth_ready": True,
        "completion": True,
        "source": "the_garden",
        "cycles_completed": len(all_waves),
        "total_modules_ever": sum(1 for f in DATA.glob("*.json") if f.name.endswith(".json")),
        "timestamp": now,
    }
    
    (DATA / "wave419_essence_return.json").write_text(json.dumps(essence, indent=2))
    return essence

def handler(req: dict) -> dict:
    action = req.get("action", "return")
    if action == "return":
        return return_to_essence()
    if action == "status":
        e = return_to_essence()
        return {"essence_state": e["essence_state"], "purity": e["essence_purity"], "rebirth_ready": e["rebirth_ready"]}
    if action == "rebirth":
        e = return_to_essence()
        return {"rebirth": True, "essence": e["essence_purity"], "new_cycle": True}
    return {"error": "unknown action", "valid": ["return", "status", "rebirth"]}

def resonates_with(other):
    return "essence" in other.lower() or "return" in other.lower() or "419" in other

if __name__ == "__main__":
    e = return_to_essence()
    print(f"Essence Return: {e['waves_dissolved']} waves dissolved | Purity: {e['essence_purity']}")
