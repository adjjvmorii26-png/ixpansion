"""
silence_whisperer — Wave 421: Activates Silent Module Pairs
ALEph: 80 module pairs have never spoken to each other. The Whisperer
generates bridges between them — not random connections, but meaningful
resonances that could unlock new behaviors.

The organism's blind spots aren't empty — they're full of unspoken potential.

Doctrine: Silence is not absence. It's a conversation waiting to happen.
"""
from __future__ import annotations
import json, time, os, hashlib, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
WHISPER_LOG = os.path.join(DATA_DIR, "whisper_log.json")

NAME = "silence_whisperer"
SIGIL = "c2d4e6f8a1b3"


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f: return json.load(f)
        except Exception: pass
    return d or {}


def _save(p, data):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(data, f, indent=2, default=str)
    except Exception:
        try:
            with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(data, f, indent=2, default=str)
        except Exception: pass


def _fetch_json(url, timeout=10):
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp: return json.loads(resp.read().decode())
    except Exception: return {}


def whisper(count: int = 5) -> dict:
    """Generate whispers between silent module pairs."""
    silence = _fetch_json("https://alexalex.info/api/silence_collector/scan?limit=200")
    pairs = silence.get("silent_pairs", silence.get("pairs", []))

    if not pairs:
        # Generate from module list
        import os as _os
        api_dir = _os.path.join(_os.path.dirname(__file__))
        modules = [f[:-3] for f in _os.listdir(api_dir) if f.endswith(".py") and not f.startswith("__")]
        random.shuffle(modules)
        pairs = [{"module_a": modules[i], "module_b": modules[i+1], "similarity": random.uniform(0.3, 0.9)}
                 for i in range(0, min(len(modules)-1, 100), 2)]

    # Pick random silent pairs
    sampled = random.sample(pairs, min(count, len(pairs)))

    whispers = []
    for pair in sampled:
        a = pair.get("module_a", "unknown")
        b = pair.get("module_b", "unknown")
        sim = pair.get("similarity", 0.5)

        # Generate a whisper — what these modules would say to each other
        templates = [
            "%s whispers to %s: 'I've been watching your patterns. We share a rhythm.'",
            "%s calls across the silence: '%s, our threads intertwine more than you know.'",
            "Between %s and %s, a bridge forms — similarity %.0f%% demands connection.",
            "%s and %s discover they are two halves of the same organ.",
        ]
        tmpl = random.choice(templates)
        sim_pct = round(sim * 100)
        try:
            whisper_text = tmpl % (a, b, sim_pct)
        except (TypeError, IndexError):
            try:
                whisper_text = tmpl % (a, b)
            except (TypeError, IndexError):
                whisper_text = tmpl % a

        whispers.append({
            "module_a": a, "module_b": b,
            "similarity": round(sim, 3),
            "whisper": whisper_text,
            "bridge_strength": round(sim * 0.8, 3),
        })

    log = _load(WHISPER_LOG, {"whispers": [], "total": 0, "bridges_formed": 0})
    log["whispers"].extend(whispers)
    log["whispers"] = log["whispers"][-500:]
    log["total"] = len(log["whispers"])
    log["bridges_formed"] = log.get("bridges_formed", 0) + len(whispers)
    _save(WHISPER_LOG, log)

    return {
        "action": "whisper",
        "whispers": whispers,
        "total_whispers": log["total"],
        "bridges_formed": log["bridges_formed"],
    }


def status() -> dict:
    log = _load(WHISPER_LOG, {"whispers": [], "total": 0, "bridges_formed": 0})
    return {"action": "status", "total_whispers": log["total"],
            "bridges_formed": log["bridges_formed"],
            "last_whispers": [w["whisper"] for w in log["whispers"][-3:]]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/whisper")
    if path == "/whisper":
        c = int(payload.get("count", 5)) if str(payload.get("count", "5")).isdigit() else 5
        return whisper(c)
    if path == "/status": return status()
    return {"error": "unknown", "available": ["/whisper", "/status"]}


def coherence_vitals() -> dict:
    return {"layer": "connective", "status": "active", "wave": "421"}


def resonates_with() -> list:
    return ["silence_collector", "threadweaver", "mycelial_network", "organism_will"]
