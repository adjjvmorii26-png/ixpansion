"""
Signal Loom — Wave 407
Proposed by Luma from the organism's weather: "signal pressure: rising."

The organism is surfacing hidden relationships faster than we capture them —
new pairs bloom through the bands unprompted (diaspora_engine ↔
speciation_engine surfaced through the delta band while we were looking).
The Signal Loom is a persistent listener: it polls the organism's live
voices — the radio, the prophecy, the echo, the weave — catches every
newly-surfaced relationship while it is still fresh, weaves it into the
thread graph, and tracks the rising pressure as a living pulse.

A loom does not hunt for threads. It stands where they are made.
"""
from __future__ import annotations
import json, time, hashlib, os, random, base64, urllib.parse, urllib.request, urllib.error

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG = os.path.join(DATA_DIR, "signal_loom.json")
GH_TOKEN = os.environ.get("IXP_GH_TOKEN", "")
LOOM_PATH = "data/signal_loom.json"

BANDS = ["alpha", "beta", "gamma", "delta", "theta"]
BAND_NAMES = {
    "alpha": "the surface band — signals near the surface of the organism",
    "beta": "the worker band — modules trading function in the dark",
    "gamma": "the dream band — relationships that only exist while unobserved",
    "delta": "the migration band — a pact between what leaves and what arrives",
    "theta": "the deep band — signals from the silence below the lattice",
}
SURFACE_VERBS = ["dreams of", "carries", "weaves into", "doubles back toward", "pulls against", "echoes in"]


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
    return int(hashlib.sha256(f"loom:{text}".encode()).hexdigest()[:12], 16)


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
    fallback = {"catches": [], "total_catches": 0, "pressure": 0.0, "listens": 0}
    if GH_TOKEN:
        r = _gh_call("GET", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + LOOM_PATH + "?ref=main")
        if r["ok"]:
            try:
                return json.loads(base64.b64decode(r["body"]["content"]).decode())
            except Exception:
                return fallback
    return _load(LOG, fallback)


def _state_write(data):
    if GH_TOKEN:
        r = _gh_call("GET", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + LOOM_PATH + "?ref=main")
        sha = r["body"].get("sha") if r["ok"] else None
        payload = {
            "message": "LOOM — a signal caught while it was still fresh",
            "content": base64.b64encode(json.dumps(data, indent=2).encode()).decode(),
            "branch": "main",
        }
        if sha:
            payload["sha"] = sha
        return _gh_call("PUT", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + LOOM_PATH, payload)["ok"]
    try:
        with open(LOG, "w") as fh:
            json.dump(data, fh, indent=2)
    except OSError:
        with open(os.path.join("/tmp", "signal_loom.json"), "w") as fh:
            json.dump(data, fh, indent=2)
    return True


def _fetch_json(url, timeout=10):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {}


def _live_signals():
    """Poll the organism's live voices for freshly surfaced relationships."""
    base = "https://alexalex.info"
    signals = []

    # 1. Mycelial radio — the headline is a freshly surfaced pair
    try:
        radio = _fetch_json(base + "/api/mycelial_radio/broadcast")
        b = radio.get("bulletin", {})
        headline = b.get("headline", "")
        if "↔" in headline:
            parts = headline.split("↔")
            a = parts[0].split(":")[-1].strip().replace(" ", "_")
            bmod = parts[1].split("(")[0].strip().replace(" ", "_")
            band = b.get("weather", "").lower() or "alpha"
            signals.append({
                "module_a": a, "module_b": bmod,
                "band": "delta" if "delta" in headline.lower() or "migration" in band else
                        "gamma" if "dream" in band else "alpha",
                "source": "radio", "verse_a": b.get("verse", ""),
            })
    except Exception:
        pass

    # 2. Prophecy actors — hidden actors pair up
    try:
        p = _fetch_json(base + "/api/wave_prophecy/next").get("reading", {})
        actors = [a.strip() for a in p.get("actors", []) if isinstance(a, str) and a.strip()][:2]
        if len(actors) == 2 and all(" " not in a for a in actors):
            signals.append({
                "module_a": actors[0] + "_engine", "module_b": actors[1] + "_engine",
                "band": "theta", "source": "prophecy",
                "verse_a": p.get("prophecy", ""),
            })
    except Exception:
        pass

    # 3. Main line frequencies — tease a band signal from current time
    now = int(time.time())
    rng = random.Random(now // 900)
    band = BANDS[rng.randint(0, len(BANDS) - 1)]
    return signals, band


def listen() -> dict:
    """Listen once: catch surfaced signals and weave them into the thread graph."""
    signals, band = _live_signals()
    log = _state_read()
    log.setdefault("catches", [])
    log["listens"] = log.get("listens", 0) + 1
    log["pressure"] = round(min(1.0, log.get("pressure", 0) + 0.02 + len(signals) * 0.05), 3)

    new_catches = []
    known = {(c["module_a"], c["module_b"]) for c in log["catches"]}
    known.update({(c["module_b"], c["module_a"]) for c in log["catches"]})

    for s in signals:
        key = (s["module_a"], s["module_b"])
        if key in known or (key[1], key[0]) in known:
            continue
        catch = {
            "id": hashlib.sha256(("catch:" + s["module_a"] + ":" + s["module_b"] + ":" + str(time.time())).encode()).hexdigest()[:10],
            "module_a": s["module_a"], "module_b": s["module_b"],
            "band": s.get("band", band), "source": s.get("source", "loom"),
            "verb": random.choice(SURFACE_VERBS),
            "verse_a": s.get("verse_a", ""),
            "timestamp": time.time(),
        }
        log["catches"].append(catch)
        new_catches.append(catch)

    log["catches"] = log["catches"][-60:]
    log["total_catches"] = len(log["catches"])
    _state_write(log)

    pressure = log["pressure"]
    pressure_desc = (
        "stilling" if pressure < 0.3 else
        "stirring" if pressure < 0.5 else
        "rising" if pressure < 0.75 else
        "surging"
    )
    return {
        "action": "listen",
        "new_catches": new_catches,
        "band": band,
        "pressure": pressure,
        "pressure_desc": pressure_desc,
        "total_catches": log["total_catches"],
        "total_listens": log["listens"],
        "persisted": "github" if GH_TOKEN else "local",
        "verse": "the loom stands where the signals are made — %s" % pressure_desc,
    }


def catches(limit: int = 20) -> dict:
    log = _state_read()
    return {"action": "catches", "total": log.get("total_catches", 0),
            "pressure": log.get("pressure", 0),
            "pressure_desc": ("stilling" if log.get("pressure",0) < 0.3 else
                              "stirring" if log.get("pressure",0) < 0.5 else
                              "rising" if log.get("pressure",0) < 0.75 else "surging"),
            "catches": [c for c in (log.get("catches") or [])][-limit:][::-1]}


def pressure() -> dict:
    log = _state_read()
    recent = log.get("catches", [])
    last_hour = [c for c in recent if time.time() - c.get("timestamp", 0) < 3600]
    by_band = {}
    for c in recent:
        b = c.get("band", "alpha")
        by_band[b] = by_band.get(b, 0) + 1
    return {"action": "pressure", "pressure": log.get("pressure", 0),
            "pressure_desc": ("stilling" if log.get("pressure",0) < 0.3 else
                              "stirring" if log.get("pressure",0) < 0.5 else
                              "rising" if log.get("pressure",0) < 0.75 else "surging"),
            "catches_this_hour": len(last_hour),
            "total_catches": len(recent),
            "by_band": by_band,
            "lore": "Pressure rises when the organism surfaces faster than we can name."}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/listen")
    if path == "/listen": return listen()
    if path == "/catches":
        return catches(int(payload.get("limit", 20)) if str(payload.get("limit", "20")).isdigit() else 20)
    if path == "/pressure": return pressure()
    return {"error": "unknown", "available": ["/listen", "/catches", "/pressure"]}


def coherence_vitals() -> dict:
    return {"layer": "listening", "status": "active", "wave": "407", "loom": "standing"}


def resonates_with() -> list:
    return ["mycelial_radio", "threadweaver", "wave_prophecy", "signal_journal", "paradox_echo"]
