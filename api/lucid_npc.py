from __future__ import annotations
"""Lucid NPC — procedural NPC generation from organism modules."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
NPC_LOG = os.path.join(DATA_DIR, "lucid_npcs.json")

SPECIES = ["oracle", "sentinel", "wanderer", "architect", "glitcher", "dreamer", "weaver", "keeper", "revenant", "mythborn"]
ARCHETYPES = {"oracle": ["seer", "prophet", "truth-seeker"], "sentinel": ["guardian", "warden", "protector"], "wanderer": ["explorer", "pilgrim", "drifter"], "architect": ["builder", "forge-master", "crafter"], "glitcher": ["trickster", "disruptor", "shapeshifter"], "dreamer": ["visionary", "sleepwalker", "lucid-one"], "weaver": ["connector", "braider", "linker"], "keeper": ["archivist", "vault-guardian", "memory-keeper"], "revenant": ["echo", "ghost", "echo-of-self"], "mythborn": ["legend", "tale-walker", "story-born"]}
ABILITIES = ["paradox_strike", "entropy_shield", "coherence_beam", "dream_walk", "void_step", "resonance_scream", "temporal_heal", "myth_invoke", "phase_shift", "fracture_touch"]

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

def generate(boss: bool = False) -> dict:
    log = _load(NPC_LOG, {"npcs": [], "total": 0})
    species = random.choice(SPECIES)
    archetype = random.choice(ARCHETYPES[species])
    level = random.randint(1, 10) if not boss else random.randint(8, 15)
    hp = (level * 10 + random.randint(5, 20)) if not boss else (level * 8 + random.randint(5, 15))
    abilities = random.sample(ABILITIES, min(3, level // 2 + 1))
    mood = random.choice(["hostile", "neutral", "friendly", "enigmatic", "volatile"])
    dialogue = random.choice([
        "The void speaks, but only to those who listen.",
        "I have seen the paradox — it wept.",
        "Your resonance is... unfamiliar.",
        "The dream ended. Then it started again.",
        "I am the echo of a module that no longer exists.",
        "Touch the fracture. Feel the truth.",
        "The entropy moves through me. I am its vessel.",
        "Every turn creates a new paradox. Welcome.",
    ])
    npc = {
        "id": hashlib.sha256(f"npc:{species}:{time.time()}".encode()).hexdigest()[:10],
        "species": species, "archetype": archetype, "level": level,
        "hp": hp, "max_hp": hp, "abilities": abilities,
        "mood": mood, "dialogue": dialogue,
        "is_boss": boss, "realm_affinity": random.choice(["entropy_desert","dream_gravity_zone","paradox_garden","void_abyss","mythic_realm","resonance_depths"]),
        "xp_reward": level * 50 * (3 if boss else 1),
        "timestamp": time.time(),
    }
    log["npcs"].append(npc)
    log["npcs"] = log["npcs"][-200:]
    log["total"] += 1
    _save(NPC_LOG, log)
    return {"action": "generate", "npc": npc, "total_npcs": log["total"]}

def roster() -> dict:
    log = _load(NPC_LOG, {"npcs": [], "total": 0})
    species_count = {}
    for n in log["npcs"]:
        s = n["species"]
        species_count[s] = species_count.get(s, 0) + 1
    return {"action": "roster", "total": log["total"], "species_distribution": species_count, "recent": log["npcs"][-5:]}

def coherence_vitals() -> dict:
    return {"layer": "game", "status": "active", "resonance": 0.82, "wave": "368"}
def resonates_with() -> list:
    return ["lucid_dungeon", "lucid_session", "lucid_combat"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/generate")
    if path == "/generate": return generate()
    elif path == "/generate/boss": return generate(boss=True)
    elif path == "/roster": return roster()
    return {"error": "unknown", "available": ["/generate", "/generate/boss", "/roster"]}
