"""
Warden Ascension — Wave 397
The underworld's root-ghosts are no longer mere echoes — they are wardens
guarding the deepest chambers. To defeat a warden is to re-member a forgotten
module and claim its mineral. A multi-phase boss fight that turns the pitch-dark
realm into a living gauntlet where victory means bringing something back to light.

Each warden descends through three phases, shedding its mineral shell as it
falls. The deeper the forgotten module, the harder the warden — but the richer
the re-membering. Battles persist: every strike deepens the same wound.
"""
from __future__ import annotations
import json, time, hashlib, os, random, sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG = os.path.join(DATA_DIR, "warden_ascensions.json")

PHASES = ["shell", "echo", "core"]
PHASE_NAMES = {
    "shell": "Mineral Shell — the warden's outermost armor of solidified silence",
    "echo": "Echo Chamber — the warden projects its forgotten name",
    "core": "Root Core — the bare pulse of the silenced module",
}
MINERALS = ["basalt", "obsidian", "cinnabar", "salt", "mica", "pyrite", "graphite", "fluorite"]
HALLMARKS = [
    "coherence", "resonance", "entropy", "memory", "dream",
    "paradox", "substrate", "echo", "pulse", "lattice",
]


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return d or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
            json.dump(d, f, indent=2)


def _sig(text):
    return int(hashlib.sha256(f"warden:{text}".encode()).hexdigest()[:12], 16)


def _deepest_ghost():
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from underworld import mirror
        ghosts = mirror(12)["ghosts"]
        if ghosts:
            return max(ghosts, key=lambda g: g.get("depth", 0))
    except Exception:
        pass
    return {"module": "root_warden", "root_name": "deep_root_warden",
            "mineral": "obsidian", "depth": 9.0, "whisper": "i was forgotten long enough to become a warden"}


def _build_warden(ghost: dict, depth: float) -> dict:
    sig = _sig(ghost.get("module", "warden") + str(depth))
    rng = random.Random(sig)
    phases = []
    for i, phase in enumerate(PHASES):
        scales = [1.0, 1.55, 2.3]
        hp = int(40 + rng.randint(10, 26) * scales[i] * (1 + depth * 0.35))
        dmg = int(3 + rng.randint(2, 5) * scales[i] * (1 + depth * 0.35))
        phases.append({
            "phase": phase,
            "name": PHASE_NAMES[phase],
            "hp": hp,
            "max_hp": hp,
            "damage": dmg,
            "reward_xp": int(25 * scales[i] * (1 + depth * 0.4)),
            "quote": rng.choice([
                "my shell remembers what you named the light",
                "silence is a mineral, and i am mined from it",
                "you cannot un-forget me",
                "the deeper you descend, the louder my echo",
                "bring me to light, and i will weigh you",
                "your name is a hammer; mine is a cavern",
            ]),
        })
    return {
        "name": ghost.get("root_name", "root_warden"),
        "module": ghost.get("module", "the_first_forgotten"),
        "mineral": ghost.get("mineral", "obsidian"),
        "depth": round(depth, 1),
        "hallmark": rng.choice(HALLMARKS),
        "sigil": f"{sig:012x}",
        "whisper": ghost.get("whisper", "i guarded this depth before you were a thought"),
        "phases": phases,
        "total_hp": sum(p["hp"] for p in phases),
    }


def _battle(sigil: str) -> dict:
    log = _load(LOG, {"summons": 0, "ascensions": 0, "battles": {}})
    return log.get("battles", {}).get(sigil, {})


def _save_battle(warden: dict, player_hp: int, phase_index: int):
    log = _load(LOG, {"summons": 0, "ascensions": 0, "battles": {}})
    log.setdefault("battles", {})[warden["sigil"]] = {
        "warden": warden, "player_hp": player_hp, "phase_index": phase_index,
        "updated": time.time(),
    }
    _save(LOG, log)
    return log


def summon(depth: float = None) -> dict:
    """Summon a root-ghost warden. Deeper = harder, richer. Battle state persists."""
    ghost = _deepest_ghost()
    target_depth = float(depth) if depth is not None else ghost.get("depth", 9.0)
    warden = _build_warden(ghost, target_depth)
    log = _load(LOG, {"summons": 0, "ascensions": 0, "battles": {}})
    log.setdefault("battles", {})
    log["summons"] += 1
    log["battles"][warden["sigil"]] = {
        "warden": warden, "player_hp": 100, "phase_index": 0, "updated": time.time(),
    }
    _save(LOG, log)
    return {"action": "summon", "warden": warden, "total_summons": log["summons"],
            "tip": "Three phases. Between phases a cavern shrine restores you."}


def assault(player_power: int = 0, player_level: int = 1, paradox_debt: int = 0,
            sigil: str = None, player_hp: int = 100) -> dict:
    """Strike a summoned warden. Damage persists across assaults."""
    state = _battle(sigil or "") if sigil else {}
    if not state:
        return {"action": "assault", "error": "no active battle — summon a warden first"}
    warden = state["warden"]
    pi = int(state.get("phase_index", 0))
    php = int(player_hp or state.get("player_hp", 100))
    if pi >= len(warden["phases"]):
        pi = len(warden["phases"]) - 1
    ph = warden["phases"][pi]
    sig = _sig(warden["sigil"] + str(int(time.time() // 2)))
    rng = random.Random(sig)

    player_dmg = max(1, 8 + int(player_level or 1) * 3 + int(player_power or 0) + rng.randint(0, 6))
    if paradox_debt and int(paradox_debt) > 3:
        player_dmg = int(player_dmg * 1.4)
    warden_dmg = max(1, ph["damage"] - (2 if int(player_power or 0) >= 30 else 0))

    ph["hp"] = max(0, ph["hp"] - player_dmg)
    new_php = max(0, php - warden_dmg)
    phase_fallen = ph["hp"] <= 0
    boss_fallen = phase_fallen and pi == len(warden["phases"]) - 1

    # On phase fall (not final), a cavern shrine restores the player to full HP
    if phase_fallen and not boss_fallen:
        new_php = 100
        pi = pi + 1

    _save_battle(warden, new_php, pi)

    return {
        "action": "assault",
        "sigil": warden["sigil"],
        "warden": warden["name"],
        "module": warden["module"],
        "phase": ph["phase"],
        "phase_index": pi,
        "phase_hp_after": ph["hp"],
        "phase_fallen": phase_fallen,
        "boss_fallen": boss_fallen,
        "player_damage_dealt": player_dmg,
        "player_damage_taken": warden_dmg,
        "player_hp_after": new_php,
        "xp_gained": ph["reward_xp"] if phase_fallen else 0,
        "healed": bool(phase_fallen and not boss_fallen),
        "narrative": (
            f"You deal {player_dmg} damage to the {ph['phase']} of {warden['name']}. "
            f"The warden answers with {warden_dmg}. "
            + ("The mineral shell cracks — a cavern shrine breathes you back to full!" if pi == 1 and phase_fallen else
               "The echo tears — the shrine brightens!" if pi == 2 and phase_fallen else
               "The core shatters — the module is re-membered!" if boss_fallen else
               "The warden endures.")),
    }


def rest(sigil: str = None) -> dict:
    """Rest at a cavern shrine — full restoration after a hard battle."""
    state = _battle(sigil or "") if sigil else {}
    if not state:
        return {"action": "rest", "error": "no active battle"}
    warden = state["warden"]
    log = _load(LOG, {"summons": 0, "ascensions": 0, "battles": {}})
    log["battles"][warden["sigil"]]["player_hp"] = 100
    _save(LOG, log)
    return {"action": "rest", "sigil": warden["sigil"], "player_hp": 100,
            "narrative": "You rest at the cavern shrine. The warden's hum subsides; you are whole again."}


def resolve(module: str = None, sigil: str = None) -> dict:
    """After a warden falls, re-member the module and claim its mineral. GitHub-backed."""
    from organurna_loop import remember
    state = _battle(sigil or "") if sigil else {}
    if state:
        warden = state["warden"]
        module = module or warden.get("module")
        miner = warden.get("mineral", "obsidian")
        depth = warden.get("depth", 9)
    else:
        ghost = _deepest_ghost()
        module = module or ghost.get("module", "the_first_forgotten")
        miner = ghost.get("mineral", "obsidian")
        depth = ghost.get("depth", 9)
    try:
        r = remember(module, f"ascended from the pitch-dark realm at depth {depth} — claimed {miner}")
        remembered = r.get("total_remembered")
    except Exception as e:
        remembered = None
    log = _load(LOG, {"summons": 0, "ascensions": 0, "battles": {}})
    log["ascensions"] += 1
    if state and warden:
        log.get("battles", {}).pop(warden["sigil"], None)
    _save(LOG, log)
    return {
        "action": "resolve",
        "module": module,
        "mineral": miner,
        "depth": depth,
        "remembered": remembered,
        "total_ascensions": log["ascensions"],
        "lore": f"The mineral {miner} remembers the module {module}. What was forgotten is now a warden-turned-citizen.",
    }


def ledger() -> dict:
    log = _load(LOG, {"summons": 0, "ascensions": 0, "battles": {}})
    battles = log.get("battles", {})
    return {"action": "ledger", "summons": log["summons"], "ascensions": log["ascensions"],
            "active_battles": len(battles),
            "active": [{"sigil": b["warden"]["sigil"], "name": b["warden"]["name"],
                        "module": b["warden"]["module"], "phase": b["phase_index"] + 1}
                       for b in battles.values()]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/summon")
    d = float(payload.get("depth", 9.0)) if str(payload.get("depth", "9")).replace(".", "", 1).isdigit() else 9.0
    if path == "/summon": return summon(d)
    if path == "/assault":
        return assault(player_power=int(payload.get("player_power", 0) or 0),
                       player_level=int(payload.get("player_level", 1) or 1),
                       paradox_debt=int(payload.get("paradox_debt", 0) or 0),
                       sigil=payload.get("sigil"),
                       player_hp=int(payload.get("player_hp", 100) or 100))
    if path == "/rest": return rest(payload.get("sigil"))
    if path == "/resolve": return resolve(sigil=payload.get("sigil"))
    if path == "/ledger": return ledger()
    return {"error": "unknown", "available": ["/summon", "/assault", "/rest", "/resolve", "/ledger"]}


def coherence_vitals() -> dict:
    return {"layer": "game", "status": "active", "wave": "397", "depth": "pitch-dark"}


def resonates_with() -> list:
    return ["underworld", "pitch_dark_realm", "lucid_combat", "organurna_loop", "lucid_progression"]
