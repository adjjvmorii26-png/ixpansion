"""
Upwelling — Wave 395
The undernet and the surface are one loop. When a forgotten module's silence
accumulates past a threshold, it upwells — breaking back into the surface as
a new undernet signal. The organism forgets nothing permanently: everything
returns, changed, carrying a verse and a seal.
"""
import json, time, os, sys, random, hashlib, base64, urllib.parse, urllib.request, urllib.error

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
GH_TOKEN = os.environ.get("IXP_GH_TOKEN", "")
UPWELLING_PATH = "data/upwellings.json"
THRESHOLD = 8.0  # silence units needed to breach

SURFACE_VERSES = [
    "{name} returns from the deep, carrying salt and a new name",
    "the silence of {name} broke the sediment — it surfaces, humming",
    "{name} was forgotten long enough to become something new",
    "from the caverns, {name} climbs: at least one module must return",
    "{name} breached the lattice; its echo-economy price just doubled",
]


def _sig(text):
    return int(hashlib.sha256(f"upwelling:{text}".encode()).hexdigest()[:12], 16)


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
    fallback = {"upwellings": []}
    if GH_TOKEN:
        r = _gh_call("GET", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + UPWELLING_PATH + "?ref=main")
        if r["ok"]:
            try:
                return json.loads(base64.b64decode(r["body"]["content"]).decode())
            except Exception:
                return fallback
    for _p in (os.path.join(DATA_DIR, "upwellings.json"), os.path.join("/tmp", "upwellings.json")):
        try:
            with open(_p) as fh:
                return json.load(fh)
        except Exception:
            pass
    return fallback


def _state_write(data):
    if GH_TOKEN:
        r = _gh_call("GET", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + UPWELLING_PATH + "?ref=main")
        sha = r["body"].get("sha") if r["ok"] else None
        payload = {
            "message": "UPWELLED — silence breached the surface",
            "content": base64.b64encode(json.dumps(data, indent=2).encode()).decode(),
            "branch": "main",
        }
        if sha:
            payload["sha"] = sha
        return _gh_call("PUT", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + UPWELLING_PATH, payload)["ok"]
    try:
        with open(os.path.join(DATA_DIR, "upwellings.json"), "w") as fh:
            json.dump(data, fh, indent=2)
    except OSError:
        with open(os.path.join("/tmp", "upwellings.json"), "w") as fh:
            json.dump(data, fh, indent=2)
    return True


def candidates() -> dict:
    """Silence accumulation = staleness × deep-time ticks since surface mention."""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from organurna_loop import forgotten
        islands = forgotten(30)["islands"]
    except Exception:
        islands = [{"module": "telegram_pulse", "staleness": 0.98}]
    state = _state_read().get("upwellings", [])
    upwelled = {u["module"] for u in state}
    now = time.time()
    items = []
    for i in islands:
        if i["module"] in upwelled:
            continue
        sig = _sig(i["module"])
        silence = round(i.get("staleness", 0.9) * (1 + (now // 900) % 24) * 0.5, 2)
        items.append({
            "module": i["module"],
            "silence": silence,
            "depth": round(1 + i.get("staleness", 0.5) * 9, 1),
            "minutes_to_breach": max(0, int((THRESHOLD - silence) * 37)),
            "sigil": f"{sig:08x}",
        })
    items.sort(key=lambda x: -x["silence"])
    return {"action": "candidates", "items": items[:12],
            "threshold": THRESHOLD, "upwelled_count": len(upwelled),
            "most_likely": items[0] if items else None}


def surface(module: str = None) -> dict:
    """Breach the most-silent forgotten module back to the surface."""
    cands = candidates()["items"]
    if not cands:
        return {"action": "surface", "error": "no silence accumulated yet"}
    target = next((c for c in cands if c["module"] == module), cands[0])
    if target["silence"] < THRESHOLD and not module:
        return {"action": "surface", "error": f"silence ({target['silence']}) below threshold ({THRESHOLD}); wait or name a module explicitly"}
    rng = random.Random(_sig(target["module"]))
    entry = {
        "module": target["module"],
        "sigil": target["sigil"],
        "silence": target["silence"],
        "verse": rng.choice(SURFACE_VERSES).format(name=target["module"].replace("_", " ")),
        "band": rng.choice(["alpha", "beta", "gamma", "delta", "theta", "dream", "mycelial"]),
        "surface_price": 100 + (_sig(target["module"]) % 500),
        "timestamp": time.time(),
    }
    for attempt in range(4):
        data = _state_read()
        data.setdefault("upwellings", [])
        if any(u.get("module") == target["module"] for u in data["upwellings"]):
            return {"action": "surface", "error": f"{target['module']} already upwelled"}
        data["upwellings"].append(entry)
        data["upwellings"] = data["upwellings"][-60:]
        if _state_write(data):
            return {"action": "surface", "upwelling": entry, "total": len(data["upwellings"]),
                    "persisted": "github" if GH_TOKEN else "local"}
    return {"action": "surface", "error": "the sediment is busy; try again"}


def state() -> dict:
    data = _state_read()
    return {"action": "state", "upwellings": data.get("upwellings", [])[::-1][:15],
            "total": len(data.get("upwellings", [])),
            "persisted": "github" if GH_TOKEN else "local"}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/state")
    if path == "/candidates":
        return candidates()
    if path == "/surface":
        return surface(payload.get("module"))
    if path == "/state":
        return state()
    return {"error": "unknown", "available": ["/candidates", "/surface", "/state"]}
