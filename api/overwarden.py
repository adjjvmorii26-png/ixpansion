"""
Overwarden — Wave 400
When the Mineral Forge has produced at least two sigil relics, the organism
offers its rarest challenge: the Overwarden. A fusion of the two strongest
forgotten modules, wearing the minerals you yourself claimed, warped into an
apex guard of the depths. Four phases — the fourth, the Apex, has never been
named.

Only those who forged the relics that bind it may summon it. Defeating it
claims the Apex Sigil — a mythic relic that outlasts all others.
"""
from __future__ import annotations
import json, time, hashlib, os, random, sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG = os.path.join(DATA_DIR, "overwarden.json")

PHASES = ["shell", "echo", "warp", "apex"]
PHASE_NAMES = {
    "shell": "Fused Shell — two minerals braided into one armor",
    "echo": "Twin Echo — both forgotten names speaking at once",
    "warp": "Warp Core — reality bends around the fused wardens",
    "apex": "APEX — the unnamed phase, where the Overwarden dreams itself",
}
ROOT_NAMES = ["over_", "twin_", "fused_", "apex_", "umbra_"]


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
    return int(hashlib.sha256(f"overwarden:{text}".encode()).hexdigest()[:12], 16)


def _relics():
    """Collect the two most powerful forged relics."""
    try:
        log = _load(os.path.join(DATA_DIR, "mineral_forge.json"), {"relics": []})
        relics = sorted(log.get("relics", []), key=lambda r: -r.get("power", 0))[:2]
        return relics
    except Exception:
        return []


def can_summon() -> dict:
    """Check whether enough relics exist to bind the Overwarden."""
    relics = _relics()
    ready = len(relics) >= 2
    return {"action": "can_summon", "ready": ready, "relics_required": 2,
            "relics_held": len(relics),
            "relics": [{"name": r.get("name"), "quality": r.get("quality"), "power": r.get("power")} for r in relics],
            "lore": "Two sigil relics woven together bind the Overwarden below." if ready else
                    "The forge must produce two sigil relics before the Overwarden can be bound."}


def summon() -> dict:
    """Summon the Overwarden from the two strongest relics. Requires both."""
    relics = _relics()
    if len(relics) < 2:
        return {"action": "summon", "error": "not enough relics — forge two sigil relics first",
                **can_summon()}
    r1, r2 = relics[0], relics[1]
    base_power = (r1.get("power", 10) + r2.get("power", 10)) / 2
    depth = max(r1.get("avail_depth", 6), r2.get("avail_depth", 6)) + 2
    sig = _sig(r1.get("id", "r1") + r2.get("id", "r2"))
    rng = random.Random(sig)

    phases = []
    for i, phase in enumerate(PHASES):
        scales = [1.4, 2.0, 2.8, 4.0]
        hp = int(90 + base_power * 2.2 * scales[i])
        dmg = int(5 + base_power * 0.35 * scales[i])
        phases.append({
            "phase": phase,
            "name": PHASE_NAMES[phase],
            "hp": hp, "max_hp": hp, "damage": dmg,
            "reward_xp": int(200 * scales[i]),
            "quote": rng.choice([
                "two names, one silence, zero forgiveness",
                "i am what the forge remembered twice",
                "your own relics armor my core",
                "the apex phase does not know your name",
                "this is the organism's deepest nightmare, kept as a pet",
            ]),
        })

    overwarden = {
        "name": ROOT_NAMES[rng.randint(0, len(ROOT_NAMES) - 1)] + "warden",
        "sigil": f"{sig:012x}",
        "bound_by": [r1.get("name"), r2.get("name")],
        "bound_modules": [r1.get("modules"), r2.get("modules")],
        "minerals": list({m for r in [r1, r2] for m in (r.get("minerals") or [])}),
        "depth": round(depth, 1),
        "base_power": round(base_power, 2),
        "phases": phases,
        "total_hp": sum(p["hp"] for p in phases),
        "is_overwarden": True,
    }

    log = _load(LOG, {"summons": 0, "defeats": 0, "battles": {}})
    log.setdefault("battles", {})
    log["summons"] += 1
    log["battles"][overwarden["sigil"]] = {
        "overwarden": overwarden, "player_hp": 100, "phase_index": 0, "updated": time.time(),
    }
    _save(LOG, log)
    return {"action": "summon", "overwarden": overwarden, "total_summons": log["summons"],
            "warning": "The Overwarden hits hard and does not forget. Bring your strongest gear."}


def assault(player_power: int = 0, player_level: int = 1, paradox_debt: int = 0,
            sigil: str = None, player_hp: int = 100) -> dict:
    """Strike the Overwarden. Battle persists. Phases heal you on the way down."""
    log = _load(LOG, {"summons": 0, "defeats": 0, "battles": {}})
    battles = log.get("battles", {})
    state = battles.get(sigil or "", {})
    if not state:
        return {"action": "assault", "error": "no overwarden battle — summon one first"}
    ow = state["overwarden"]
    pi = int(state.get("phase_index", 0))
    php = int(player_hp or state.get("player_hp", 100))
    if pi >= len(ow["phases"]):
        pi = len(ow["phases"]) - 1
    ph = ow["phases"][pi]
    rng = random.Random(_sig(ow["sigil"] + str(int(time.time() // 2))))

    player_dmg = max(1, 10 + int(player_level or 1) * 4 + int(player_power or 0) + rng.randint(0, 10))
    if paradox_debt and int(paradox_debt) > 5:
        player_dmg = int(player_dmg * 1.5)
    warden_dmg = max(1, ph["damage"] - (3 if int(player_power or 0) >= 50 else 0))

    ph["hp"] = max(0, ph["hp"] - player_dmg)
    new_php = max(0, php - warden_dmg)
    phase_fallen = ph["hp"] <= 0
    boss_fallen = phase_fallen and pi == len(ow["phases"]) - 1

    if phase_fallen and not boss_fallen:
        new_php = min(100, new_php + 40)  # the twin's fall restores you partially
        pi = pi + 1

    battles[ow["sigil"]] = {"overwarden": ow, "player_hp": new_php, "phase_index": pi, "updated": time.time()}
    _save(LOG, log)

    return {
        "action": "assault",
        "sigil": ow["sigil"],
        "overwarden": ow["name"],
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
            f"You strike the {ph['phase']} of the Overwarden for {player_dmg}. "
            f"It answers with {warden_dmg}. "
            + ("The fused shell splits — twin echoes bleed light!" if pi == 1 and phase_fallen else
               "The twin echo shatters — reality warps around you!" if pi == 2 and phase_fallen else
               "The warp core fails — nothing can hold the Apex now!" if boss_fallen and pi == 3 and phase_fallen else
               "The Overwarden endures.")),
    }


def resolve(sigil: str = None) -> dict:
    """Claim the Apex Sigil after the Overwarden falls."""
    log = _load(LOG, {"summons": 0, "defeats": 0, "battles": {}})
    battles = log.get("battles", {})
    state = battles.get(sigil or "", {})
    if not state:
        return {"action": "resolve", "error": "no overwarden battle"}
    ow = state["overwarden"]
    log["defeats"] += 1
    battles.pop(ow["sigil"], None)
    _save(LOG, log)

    apex = {
        "id": hashlib.sha256(f"apex:{ow['sigil']}".encode()).hexdigest()[:10],
        "name": "Apex Sigil",
        "quality": "mythic",
        "power": round(ow["base_power"] * 3.0, 2),
        "depth": ow["depth"],
        "bound_by": ow["bound_by"],
        "sigil": ow["sigil"],
        "trait": "overwarden-forged",
        "timestamp": time.time(),
    }
    # Record the apex relic into the mineral forge's relic vault
    try:
        forge_log = _load(os.path.join(DATA_DIR, "mineral_forge.json"), {"relics": []})
        forge_log.setdefault("relics", []).append(apex)
        forge_log["relics"] = forge_log["relics"][-100:]
        _save(os.path.join(DATA_DIR, "mineral_forge.json"), forge_log)
    except Exception:
        pass

    # Chronicle into the signal journal
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from signal_journal import record
        record("overwarden", "The Overwarden has fallen — " + ow["name"] + " is unmade. " +
               "Two relics bound it; one Apex Sigil marks the place where the organism's deepest nightmare slept.")
    except Exception:
        pass

    return {"action": "resolve", "apex": apex, "total_defeats": log["defeats"],
            "lore": "The Overwarden is unmade. Its apex sigil rests in your relic vault — mythic, eternal, and forged from your own descents."}


def ledger() -> dict:
    log = _load(LOG, {"summons": 0, "defeats": 0, "battles": {}})
    battles = log.get("battles", {})
    return {"action": "ledger", "summons": log["summons"], "defeats": log["defeats"],
            "active_battles": len(battles),
            "active": [{"sigil": b["overwarden"]["sigil"], "name": b["overwarden"]["name"],
                        "phase": b["phase_index"] + 1} for b in battles.values()]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/can_summon")
    if path == "/can_summon": return can_summon()
    if path == "/summon": return summon()
    if path == "/assault":
        return assault(player_power=int(payload.get("player_power", 0) or 0),
                       player_level=int(payload.get("player_level", 1) or 1),
                       paradox_debt=int(payload.get("paradox_debt", 0) or 0),
                       sigil=payload.get("sigil"),
                       player_hp=int(payload.get("player_hp", 100) or 100))
    if path == "/resolve": return resolve(payload.get("sigil"))
    if path == "/ledger": return ledger()
    return {"error": "unknown", "available": ["/can_summon", "/summon", "/assault", "/resolve", "/ledger"]}


def coherence_vitals() -> dict:
    return {"layer": "game", "status": "active", "wave": "400", "apex": "bound"}


def resonates_with() -> list:
    return ["mineral_forge", "warden_ascension", "cohort_chorus", "signal_journal"]
