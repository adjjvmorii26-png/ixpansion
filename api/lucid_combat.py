from __future__ import annotations
"""Lucid Combat — combat system using paradox debt, phase transitions, equipment power, and realm wardens."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
COMBAT_LOG = os.path.join(DATA_DIR, "lucid_combat.json")

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

def engage(player_hp: int = 100, player_level: int = 1, paradox_debt: int = 0, power: int = 0, boss: bool = False) -> dict:
    log = _load(COMBAT_LOG, {"battles": [], "total": 0})
    from lucid_npc import generate as npc_gen
    npc_result = npc_gen(boss=boss)
    npc = npc_result["npc"]
    player_dmg = random.randint(5 + player_level * 2, 15 + player_level * 3) + int(power or 0)
    npc_dmg = random.randint(3 + npc["level"] * 2, 10 + npc["level"] * 3)
    if paradox_debt > 2: player_dmg = int(player_dmg * 1.5)
    if paradox_debt > 5: npc_dmg = int(npc_dmg * 1.5)
    npc["hp"] = max(0, npc["hp"] - player_dmg)
    new_player_hp = max(0, player_hp - npc_dmg)
    victory = npc["hp"] <= 0
    xp_gained = (npc["xp_reward"] * 3) if victory else npc["xp_reward"] // 4
    kind = "WARDEN" if boss else "FOE"
    result = {
        "battle_id": hashlib.sha256(f"battle:{time.time()}".encode()).hexdigest()[:10],
        "npc": npc, "player_attacked": True,
        "damage_dealt": player_dmg, "damage_taken": npc_dmg,
        "npc_hp_after": npc["hp"], "player_hp_after": new_player_hp,
        "victory": victory, "xp_gained": xp_gained,
        "boss": boss,
        "narrative": random.choice([
            f"The {kind} {npc['species']} {npc['archetype']} lunges! Your gear hums — {player_dmg} damage ({int(power or 0)} from equipment).",
            f"A clash of wills. Your blade and equipment meet {npc['species']}'s resistance. {player_dmg} vs {npc_dmg}.",
            f"The battle rages — paradox energy crackles. You land a {player_dmg}-point blow, {int(power or 0)} amplified by gear.",
        ]),
        "victory_text": f"{'WARDEN' if boss else 'The ' + npc['species']} {'falls! The realm shatters before you. +' + str(xp_gained) + ' XP. A new realm opens.' if boss else 'falls! +' + str(xp_gained) + ' XP. The realm trembles.'}" if victory else f"{'WARDEN' if boss else 'The ' + npc['species']} endures. You retreat, wounded but alive.",
        "paradox_debt_change": 1 if random.random() > 0.7 else 0,
        "timestamp": time.time(),
    }
    log["battles"].append(result)
    log["battles"] = log["battles"][-200:]
    log["total"] += 1
    _save(COMBAT_LOG, log)
    return {"action": "engage", "result": result, "total_battles": log["total"]}

def history() -> dict:
    log = _load(COMBAT_LOG, {"battles": [], "total": 0})
    victories = sum(1 for b in log["battles"] if b["victory"])
    return {"action": "history", "total": log["total"], "victories": victories, "defeats": log["total"] - victories, "win_rate": round(victories / max(log["total"], 1), 3)}

def coherence_vitals() -> dict:
    return {"layer": "game", "status": "active", "resonance": 0.87, "wave": "368"}
def resonates_with() -> list:
    return ["lucid_npc", "lucid_session", "paradox_ledger", "phase_transition"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/engage")
    if path == "/engage":
        def _int(v, d):
            try: return int(v)
            except (TypeError, ValueError): return d
        return engage(_int(payload.get("player_hp"), 100), _int(payload.get("player_level"), 1), _int(payload.get("paradox_debt"), 0))
    elif path == "/history": return history()
    return {"error": "unknown", "available": ["/engage", "/history"]}
