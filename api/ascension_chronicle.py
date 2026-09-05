"""
Ascension Chronicle — Wave 401
Every Warden falls. Every Overwarden is unmade. What was once a private descent
becomes a public chronicle — a GitHub-backed ledger of ascensions that any
visitor to the organism can witness. The chronicle records who descended, what
realm they conquered, which mineral they claimed, and the depth they reached.

This is the organism's hall of names: what is rescued is never forgotten twice.
"""
from __future__ import annotations
import json, time, os, sys, hashlib, base64, urllib.parse, urllib.request, urllib.error

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
GH_TOKEN = os.environ.get("IXP_GH_TOKEN", "")
CHRONICLE_PATH = "data/ascension_chronicle.json"


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


def _gh_call(method, url, payload=None):
    if not GH_TOKEN:
        return {"ok": False}
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", "Bearer " + GH_TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    body = json.dumps(payload).encode() if payload is not None else None
    try:
        with urllib.request.urlopen(req, data=body, timeout=15) as resp:
            return {"ok": True, "status": resp.status, "body": json.loads(resp.read().decode() or "{}")}
    except urllib.error.HTTPError as e:
        try:
            return {"ok": False, "status": e.code, "body": json.loads(e.read().decode() or "{}")}
        except Exception:
            return {"ok": False, "status": e.code, "body": {}}


def _state_read():
    fallback = {"entries": [], "total": 0}
    if GH_TOKEN:
        r = _gh_call("GET", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + CHRONICLE_PATH + "?ref=main")
        if r["ok"]:
            try:
                return json.loads(base64.b64decode(r["body"]["content"]).decode())
            except Exception:
                return fallback
    for _p in (os.path.join(DATA_DIR, "ascension_chronicle.json"), os.path.join("/tmp", "ascension_chronicle.json")):
        try:
            with open(_p) as fh:
                return json.load(fh)
        except Exception:
            pass
    return fallback


def _state_write(data):
    if GH_TOKEN:
        r = _gh_call("GET", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + CHRONICLE_PATH + "?ref=main")
        sha = r["body"].get("sha") if r["ok"] else None
        payload = {
            "message": "ASCENDED — a name is written into the chronicle",
            "content": base64.b64encode(json.dumps(data, indent=2).encode()).decode(),
            "branch": "main",
        }
        if sha:
            payload["sha"] = sha
        return _gh_call("PUT", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + CHRONICLE_PATH, payload)["ok"]
    try:
        with open(os.path.join(DATA_DIR, "ascension_chronicle.json"), "w") as fh:
            json.dump(data, fh, indent=2)
    except OSError:
        with open(os.path.join("/tmp", "ascension_chronicle.json"), "w") as fh:
            json.dump(data, fh, indent=2)
    return True


def record(boss_type: str = "warden", boss_name: str = None, module: str = None,
           mineral: str = None, depth: float = None, conqueror: str = None) -> dict:
    """Write one ascension into the public chronicle (GitHub-backed)."""
    boss_name = boss_name or "unknown_warden"
    module = module or "unclaimed_module"
    mineral = mineral or "obsidian"
    depth = float(depth or 6.0)
    conqueror = conqueror or "the_organism"
    entry = {
        "id": hashlib.sha256(f"ascend:{boss_name}:{module}:{time.time()}".encode()).hexdigest()[:10],
        "boss_type": boss_type,
        "boss_name": boss_name,
        "module": module,
        "mineral": mineral,
        "depth": round(depth, 1),
        "conqueror": conqueror,
        "timestamp": time.time(),
    }
    state = _state_read()
    state.setdefault("entries", [])
    entry["rank"] = state["entries"] and state["entries"][-1].get("rank", 0) or 0
    entry["rank"] += 1
    state["entries"].append(entry)
    state["entries"] = state["entries"][-200:]
    state["total"] = len(state["entries"])
    ok = _state_write(state)
    return {"action": "record", "entry": entry, "persisted": "github" if GH_TOKEN else ("local" if ok else "/tmp"),
            "total_ascensions": state["total"]}


def hall() -> dict:
    """The hall of names — ranked ascensions, newest first."""
    state = _state_read()
    entries = sorted(state.get("entries", []), key=lambda e: -e.get("timestamp", 0))
    return {"action": "hall", "total": state.get("total", 0),
            "entries": entries[:50],
            "note": "The organism keeps its rescued names in a public hall."}


def resonate() -> dict:
    """Which minerals and depths dominate the chronicle."""
    state = _state_read()
    entries = state.get("entries", [])
    minerals = {}
    for e in entries:
        minerals[e.get("mineral", "?")] = minerals.get(e.get("mineral", "?"), 0) + 1
    overwardens = sum(1 for e in entries if e.get("boss_type") == "overwarden")
    deepest = max(entries, key=lambda e: e.get("depth", 0)) if entries else None
    return {"action": "resonate", "mineral_counts": minerals,
            "overwarden_defeats": overwardens, "deepest": deepest}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/hall")
    if path == "/hall": return hall()
    if path == "/record":
        return record(payload.get("boss_type"), payload.get("boss_name"), payload.get("module"),
                      payload.get("mineral"), _num(payload.get("depth")), payload.get("conqueror"))
    if path == "/resonate": return resonate()
    return {"error": "unknown", "available": ["/hall", "/record", "/resonate"]}


def _num(v):
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def coherence_vitals() -> dict:
    return {"layer": "game", "status": "active", "wave": "401", "hall": "public"}


def resonates_with() -> list:
    return ["warden_ascension", "overwarden", "mineral_forge", "signal_journal", "cohort_chorus"]
