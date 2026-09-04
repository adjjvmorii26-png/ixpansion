from __future__ import annotations
"""Lucid Session — game session state machine. Each turn is a wave."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SESSION_LOG = os.path.join(DATA_DIR, "lucid_sessions.json")

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

def start(realm: str = None) -> dict:
    log = _load(SESSION_LOG, {"sessions": [], "total": 0})
    sid = hashlib.sha256(f"session:{time.time()}:{random.random()}".encode()).hexdigest()[:10]
    session = {
        "id": sid, "player_hp": 100, "player_max_hp": 100,
        "player_level": 1, "player_xp": 0, "player_xp_next": 200,
        "paradox_debt": 0, "coherence": 0.8,
        "wave": 0, "status": "active",
        "realm": realm or "entropy_desert",
        "current_room": "room_0",
        "inventory": [], "abilities": ["basic_attack", "coherence_shield"],
        "log": [{"event": "session_started", "realm": realm or "entropy_desert", "time": time.time()}],
        "actions_taken": 0, "enemies_defeated": 0, "treasures_found": 0,
        "timestamp": time.time(),
    }
    log["sessions"].append(session)
    log["sessions"] = log["sessions"][-50:]
    log["total"] += 1
    _save(SESSION_LOG, log)
    return {"action": "start", "session": session, "total_sessions": log["total"]}

def action(session_id: str, act: str = "explore") -> dict:
    log = _load(SESSION_LOG, {"sessions": []})
    session = next((s for s in log["sessions"] if s["id"] == session_id), None)
    if not session:
        return {"error": "session not found"}

    outcomes = {
        "explore": {"msg": "You move deeper into the realm.", "xp": random.randint(10, 30)},
        "attack": {"msg": "You strike at the darkness!", "xp": random.randint(20, 50), "hp_change": random.randint(-10, -3)},
        "defend": {"msg": "You raise your coherence shield.", "xp": random.randint(5, 15), "hp_change": random.randint(0, 5)},
        "rest": {"msg": "You rest in the resonance.", "hp_change": random.randint(10, 25), "xp": 5},
        "use_treasure": {"msg": "The treasure resonates with your soul.", "coherence_change": round(random.uniform(0.05, 0.15), 3)},
        "paradox_resist": {"msg": "You resist the paradox... but it takes its toll.", "paradox_change": -1, "hp_change": random.randint(-5, 0), "xp": 30},
        "paradox_embrace": {"msg": "You embrace the paradox. Power floods through you.", "paradox_change": 1, "xp": random.randint(40, 80), "coherence_change": -0.1},
    }
    o = outcomes.get(act, outcomes["explore"])
    session["wave"] += 1
    session["actions_taken"] += 1
    session["player_xp"] += o.get("xp", 0)
    if "hp_change" in o: session["player_hp"] = max(1, min(session["player_max_hp"], session["player_hp"] + o["hp_change"]))
    if "paradox_change" in o: session["paradox_debt"] = max(0, session["paradox_debt"] + o["paradox_change"])
    if "coherence_change" in o: session["coherence"] = round(max(0, min(1, session["coherence"] + o["coherence_change"])), 3)
    if session["player_xp"] >= session["player_xp_next"]:
        session["player_level"] += 1
        session["player_xp_next"] = int(session["player_xp_next"] * 1.5)
        session["player_max_hp"] += 10
        session["player_hp"] = session["player_max_hp"]
        o["msg"] += f" LEVEL UP! Now level {session['player_level']}!"
    if session["player_hp"] <= 0:
        session["status"] = "defeated"
        o["msg"] += " You have fallen..."
    if random.random() > 0.8:
        session["treasures_found"] += 1
        session["inventory"].append(random.choice(["probability_lens", "dream_seed", "paradox_compass", "coherence_mirror", "void_anchor", "temporal_crystal", "myth_tablet", "resonance_key", "repair_salve", "synchronicity_beacon"]))
        o["msg"] += " [Found: " + session["inventory"][-1] + "]"
    event = {"event": act, "wave": session["wave"], "msg": o["msg"], "time": time.time()}
    session["log"].append(event)
    _save(SESSION_LOG, log)
    return {"action": "action", "session": session, "outcome": o["msg"]}

def status(session_id: str) -> dict:
    log = _load(SESSION_LOG, {"sessions": []})
    session = next((s for s in log["sessions"] if s["id"] == session_id), None)
    if not session: return {"error": "session not found"}
    return {"action": "status", "session": session}

def coherence_vitals() -> dict:
    return {"layer": "game", "status": "active", "resonance": 0.92, "wave": "368"}
def resonates_with() -> list:
    return ["lucid_dungeon", "lucid_npc", "lucid_physics_rules", "lucid_lore", "lucid_combat"]

def _encode_session(session):
    import base64
    return base64.urlsafe_b64encode(json.dumps(session).encode()).decode()

def _decode_session(blob):
    import base64
    try:
        padded = blob + "=" * (-len(blob) % 4)
        return json.loads(base64.urlsafe_b64decode(padded.encode()).decode())
    except Exception:
        return None

def action_stateless(blob: str, act: str = "explore") -> dict:
    session = _decode_session(blob)
    if not session:
        return {"action": "action", "error": "invalid session blob"}
    result = _apply_action(session, act)
    session = result["session"]
    return {"action": "action", "outcome": result["outcome"], "session": session, "blob": _encode_session(session)}

def _apply_action(session, act):
    outcomes = {
        "explore": {"msg": "You move deeper into the realm.", "xp": 20},
        "attack": {"msg": "You strike at the darkness!", "xp": 35, "hp_change": -6},
        "defend": {"msg": "You raise your coherence shield.", "xp": 10, "hp_change": 2},
        "rest": {"msg": "You rest in the resonance.", "hp_change": 18, "xp": 5},
        "use_treasure": {"msg": "The treasure resonates with your soul.", "coherence_change": 0.1},
        "paradox_resist": {"msg": "You resist the paradox... but it takes its toll.", "paradox_change": -1, "hp_change": -3, "xp": 30},
        "paradox_embrace": {"msg": "You embrace the paradox. Power floods through you.", "paradox_change": 1, "xp": 60, "coherence_change": -0.1},
        "flee": {"msg": "You retreat to the entrance, breathing hard.", "xp": 5},
    }
    o = outcomes.get(act, outcomes["explore"])
    session["wave"] += 1
    session["actions_taken"] += 1
    session["player_xp"] += o.get("xp", 0)
    if "hp_change" in o: session["player_hp"] = max(1, min(session["player_max_hp"], session["player_hp"] + o["hp_change"]))
    if "paradox_change" in o: session["paradox_debt"] = max(0, session["paradox_debt"] + o["paradox_change"])
    if "coherence_change" in o: session["coherence"] = round(max(0, min(1, session["coherence"] + o["coherence_change"])), 3)
    if session["player_xp"] >= session["player_xp_next"]:
        session["player_level"] += 1
        session["player_xp_next"] = int(session["player_xp_next"] * 1.5)
        session["player_max_hp"] += 10
        session["player_hp"] = session["player_max_hp"]
        o["msg"] += f" LEVEL UP! Now level {session['player_level']}!"
    if session["player_hp"] <= 0:
        session["status"] = "defeated"
        o["msg"] += " You have fallen..."
    if random.random() > 0.8:
        session["treasures_found"] += 1
        session["inventory"].append(random.choice(["probability_lens","dream_seed","paradox_compass","coherence_mirror","void_anchor","temporal_crystal","myth_tablet","resonance_key","repair_salve","synchronicity_beacon"]))
        o["msg"] += " [Found: " + session["inventory"][-1] + "]"
    o["msg"] = f"W{session['wave']}: {o['msg']}"
    return {"outcome": o["msg"], "session": session}

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/start")
    if path == "/start":
        s = start(payload.get("realm") or payload.get("realm_name"))
        session = s["session"]
        s["blob"] = _encode_session(session)
        return s
    elif path == "/action":
        if payload.get("blob"):
            return action_stateless(payload.get("blob"), payload.get("act", "explore"))
        return action(payload.get("session_id", ""), payload.get("act", "explore"))
    elif path == "/status":
        if payload.get("blob"):
            session = _decode_session(payload.get("blob"))
            if session: return {"action": "status", "session": session}
        return status(payload.get("session_id", ""))
    return {"error": "unknown", "available": ["/start", "/action", "/status"]}
