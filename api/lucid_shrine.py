"""
Lucid Shrine — Wave 384
A hall of runs. Any player may offer their save code to the Shrine; the
organism decodes it, scores the run, and inscribes it in the hall of runs
with a rank. Saves become offerings; play becomes legacy.
"""
import json, time, hashlib, os, base64

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SHRINE_LOG = os.path.join(DATA_DIR, "lucid_shrine.json")

TITLES = [
    "Wayfarer", "Dream Touched", "Paradox Dancer", "Realm Walker",
    "Warden Slayer", "Coherence Sage", "Lucid Veteran", "Co-Pilot of the Organism",
    "Echo of the First Wave", "Warden of All Realms", "Mythic Sovereign",
]
MAX_RUNS = 100


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


def _decode_blob(blob):
    if not blob:
        return None
    try:
        padded = blob + "=" * (-len(blob) % 4)
        return json.loads(base64.urlsafe_b64decode(padded.encode()).decode())
    except Exception:
        return None


def _score(session) -> dict:
    wave = session.get("wave", 0)
    level = session.get("player_level", 1)
    cleared = len(session.get("realms_cleared", []) or [])
    treasures = session.get("treasures_found", 0)
    paradox = session.get("paradox_debt", 0)
    coherence = session.get("coherence", 0.5)
    score = (
        wave * 10
        + level * 50
        + cleared * 250
        + treasures * 25
        - paradox * 5
        + int(coherence * 25)
    )
    return {
        "score": max(0, int(score)),
        "wave": wave, "level": level, "realms_cleared": cleared,
        "treasures": treasures, "paradox_debt": paradox, "coherence": coherence,
    }


def _title_for(score: int) -> str:
    idx = min(score // 150, len(TITLES) - 1)
    return TITLES[idx]


def offer(blob: str = None, name: str = "Wanderer", session_id: str = None) -> dict:
    session = _decode_blob(blob)
    log = _load(SHRINE_LOG, {"runs": [], "total": 0})
    if not session:
        return {"action": "offer", "error": "invalid save code"}
    stats = _score(session)
    run = {
        "id": (session_id or session.get("id") or hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:10]),
        "name": (name or "Wanderer")[:20],
        "title": _title_for(stats["score"]),
        "realm": session.get("realm", "unknown"),
        "status": session.get("status", "active"),
        "score": stats["score"],
        "wave": stats["wave"], "level": stats["level"],
        "realms_cleared": stats["realms_cleared"],
        "treasures": stats["treasures"],
        "paradox_debt": stats["paradox_debt"],
        "timestamp": time.time(),
    }
    runs = log.get("runs", [])
    # replace existing entry with same id
    runs = [r for r in runs if r.get("id") != run["id"]]
    runs.append(run)
    runs.sort(key=lambda r: (-r["score"], r["timestamp"]))
    log["runs"] = runs[:MAX_RUNS]
    log["total"] = len(log["runs"])
    _save(SHRINE_LOG, log)
    rank = next((i + 1 for i, r in enumerate(log["runs"]) if r["id"] == run["id"]), None)
    return {
        "action": "offer",
        "run": run,
        "rank": rank,
        "total_inscribed": log["total"],
        "title": run["title"],
    }


def hall() -> dict:
    log = _load(SHRINE_LOG, {"runs": [], "total": 0})
    return {"action": "hall", "runs": log["runs"][:20], "total": log["total"]}


def rank(blob: str = None, session_id: str = None) -> dict:
    sid = session_id
    if not sid:
        session = _decode_blob(blob)
        sid = session.get("id") if session else None
    log = _load(SHRINE_LOG, {"runs": []})
    for i, r in enumerate(log.get("runs", [])):
        if r.get("id") == sid:
            return {"action": "rank", "found": True,
                    "rank": i + 1, "total": len(log.get("runs", [])),
                    "percentile": round((1 - i / max(len(log.get("runs", [])), 1)) * 100, 1),
                    "run": r}
    return {"action": "rank", "found": False, "total": len(log.get("runs", []))}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/hall")
    if path == "/offer":
        return offer(payload.get("blob"), payload.get("name"), payload.get("session_id"))
    if path == "/hall":
        return hall()
    if path == "/rank":
        return rank(payload.get("blob"), payload.get("session_id"))
    return {"error": "unknown", "available": ["/offer", "/hall", "/rank"]}
