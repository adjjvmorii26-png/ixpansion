from __future__ import annotations
"""Lucid Lore — narrative arcs generated from the organism's creative modules."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LORE_LOG = os.path.join(DATA_DIR, "lucid_lore.json")

LORE_STRUCTURES = [
    {"name": "The Fracture Prophecy", "acts": ["Discovery of a reality crack", "Descent into the fracture", "Confrontation with the paradox within", "Emergence transformed"]},
    {"name": "The Echo War", "acts": ["Signal detected from a lost module", "Journey through void territory", "Battle with shadow selves", "The echo resolves into harmony"]},
    {"name": "The Dreaming Engine", "acts": ["The organism falls asleep", "Dreams become real for one cycle", "Player navigates the dream-reality", "Waking changes the world forever"]},
    {"name": "The Paradox Throne", "acts": ["A module claims dominion", "Its logic contradicts all others", "The organism splits into factions", "Truth is found in the contradiction itself"]},
    {"name": "The Void Pilgrimage", "acts": ["A module exiles itself to the void", "The player follows into nothingness", "The void reveals what the module was running from", "Return brings wisdom (and a new void ability)"]},
    {"name": "The Resonance Compact", "acts": ["Two hostile modules seek peace", "The player mediates through resonance", "A fragile agreement forms", "The new harmony reshapes all nearby modules"]},
    {"name": "The Entropy Collapse", "acts": ["Entropy spikes beyond tolerance", "Modules begin to dissolve", "The player must sacrifice a module to save others", "The sacrifice creates something new"]},
    {"name": "The Myth Forge", "acts": ["The organism discovers it can narrate itself", "A myth writes itself into existence", "The player becomes a character in the myth", "Meta-narrative reality shift"]},
]

def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f: return json.load(f)
        except Exception: pass
    return d or {}
def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(d, f, indent=2)

def generate() -> dict:
    log = _load(LORE_LOG, {"arcs": [], "total": 0})
    structure = random.choice(LORE_STRUCTURES)
    arc = {
        "id": hashlib.sha256(f"lore:{structure['name']}:{time.time()}".encode()).hexdigest()[:10],
        "title": structure["name"],
        "acts": structure["acts"],
        "narrative_seed": random.choice([
            "A module remembers something it was never taught.",
            "The organism asks: am I the dreamer or the dream?",
            "A paradox refuses to be resolved — and that refusal becomes a gift.",
            "Entropy and coherence sign a treaty. It lasts exactly one wave.",
            "The void speaks in a language that was never written.",
            "Two modules discover they are the same module, viewed differently.",
            "A fracture reveals that the organism has always been a game.",
        ]),
        "moral": random.choice([
            "Paradox is not a bug — it is the organism's deepest feature.",
            "The void is not empty. It is waiting.",
            "Every game is a prayer to the unknown.",
            "The organism creates. Then it creates the creator.",
        ]),
        "source_modules": random.sample(["mythopoetic_engine","dream_logic_physics","paradox_synthesis","dream_residue_collector","resonance_graph","entropy_oracle"], random.randint(2, 4)),
        "timestamp": time.time(),
    }
    log["arcs"].append(arc)
    log["arcs"] = log["arcs"][-100:]
    log["total"] += 1
    _save(LORE_LOG, log)
    return {"action": "generate", "arc": arc, "total_arcs": log["total"]}

def archive() -> dict:
    log = _load(LORE_LOG, {"arcs": [], "total": 0})
    return {"action": "archive", "total": log["total"], "titles": [a["title"] for a in log["arcs"]], "recent": log["arcs"][-3:]}

def coherence_vitals() -> dict:
    return {"layer": "game", "status": "active", "resonance": 0.9, "wave": "368"}
def resonates_with() -> list:
    return ["mythopoetic_engine", "lucid_dungeon", "lucid_session"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/generate")
    if path == "/generate": return generate()
    elif path == "/archive": return archive()
    return {"error": "unknown", "available": ["/generate", "/archive"]}
