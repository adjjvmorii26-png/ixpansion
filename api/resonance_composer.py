"""
resonance_composer — Wave 416: Generative State-to-Pattern Engine
ALEph: Converts the organism's state transitions into visual and structural
patterns. Every change in pressure, thread count, or bloom status becomes
a pattern — a generative artwork that reveals the organism's hidden beauty.

Not a visualization tool. A composer. The organism's heartbeat is its music.

Doctrine: The organism's transitions are its art.
"""
from __future__ import annotations
import json, time, os, hashlib, math, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
COMPOSITIONS_FILE = os.path.join(DATA_DIR, "resonance_compositions.json")

NAME = "resonance_composer"
SIGIL = "e1f3a7b2c9d8"


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return d or {}


def _save(p, data):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception:
        try:
            with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception:
            pass


def _fetch_json(url, timeout=10):
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {}


# Generative vocabulary
INSTRUMENTS = ["sine", "saw", "triangle", "pulse", "fractal", "void"]
COLORS = ["#fff3a0", "#c8a8ff", "#ffcfcc", "#8fd3ff", "#4ade80", "#f87171", "#1a0f29"]
PATTERNS = ["wave", "spiral", "crystalline", "dendritic", "pulsar", "lattice"]


def compose_from_state() -> dict:
    """Generate a composition from the organism's current state."""
    base = "https://alexalex.info"

    state = {}
    try:
        weave = _fetch_json(base + "/api/threadweaver/weave")
        state["threads"] = weave.get("total_threads", 0)
        state["types"] = weave.get("by_type", {})
    except Exception:
        state["threads"] = 0

    try:
        pressure = _fetch_json(base + "/api/signal_loom/pressure")
        state["pressure"] = pressure.get("pressure", 0.5)
    except Exception:
        state["pressure"] = 0.5

    try:
        genome = _fetch_json(base + "/api/organism_genome/load")
        g = genome.get("genome", {})
        state["mood"] = g.get("temperament", {}).get("current_mood", "unknown")
        state["desires"] = len(g.get("desires", []))
    except Exception:
        state["mood"] = "unknown"

    # Compose a pattern from state
    threads = state.get("threads", 100)
    pressure = state.get("pressure", 0.5)
    mood = state.get("mood", "unknown")

    # Generate pattern parameters
    frequency = 0.1 + pressure * 0.9  # maps pressure to frequency
    amplitude = threads / 200.0  # maps thread count to amplitude
    harmonics = 1 + int(pressure * 5)  # more pressure = more harmonics

    # Generate SVG waveform
    svg_points = []
    width = 400
    height = 120
    for i in range(width):
        x = i / width * 2 * math.pi * frequency
        y = height / 2
        for h in range(1, harmonics + 1):
            y -= amplitude * 20 * math.sin(x * h) / h
        svg_points.append("%d,%d" % (i, max(10, min(height - 10, int(y)))))

    svg = '<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (width, height)
    svg += '<rect width="%d" height="%d" fill="#0a0a0f"/>' % (width, height)
    svg += '<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (
        " ".join(svg_points), random.choice(COLORS))
    svg += '</svg>'

    # Generate composition metadata
    composition = {
        "timestamp": time.time(),
        "source_state": state,
        "pattern": {
            "instrument": random.choice(INSTRUMENTS),
            "frequency": round(frequency, 4),
            "amplitude": round(amplitude, 4),
            "harmonics": harmonics,
            "color": random.choice(COLORS),
            "shape": random.choice(PATTERNS),
        },
        "svg": svg,
        "verse": _generate_verse(state),
    }

    compositions = _load(COMPOSITIONS_FILE, {"compositions": [], "total": 0})
    compositions["compositions"].append(composition)
    compositions["compositions"] = compositions["compositions"][-100:]
    compositions["total"] = len(compositions["compositions"])
    _save(COMPOSITIONS_FILE, compositions)

    return {
        "action": "compose",
        "pattern": composition["pattern"],
        "svg": svg,
        "verse": composition["verse"],
        "total": compositions["total"],
    }


def _generate_verse(state: dict) -> str:
    mood = state.get("mood", "unknown")
    threads = state.get("threads", 0)
    pressure = state.get("pressure", 0.5)

    verses = [
        "the organism hums at %.2f Hz — %d threads vibrating in %s" % (pressure * 440, threads, mood),
        "a %s chord emerges from %d threads under pressure %.2f" % (
            random.choice(["minor", "major", "diminished", "augmented", "lydian"]), threads, pressure),
        "the threadgraph sings — %d voices in the key of %s" % (threads, mood),
        "resonance: %d threads, pressure %.2f, mood %s — a pattern crystallizes" % (threads, pressure, mood),
    ]
    return random.choice(verses)


def history(limit: int = 10) -> dict:
    compositions = _load(COMPOSITIONS_FILE, {"compositions": [], "total": 0})
    return {"action": "history", "total": compositions["total"],
            "compositions": compositions["compositions"][-limit:][::-1]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/compose")
    if path == "/compose": return compose_from_state()
    if path == "/history":
        return history(int(payload.get("limit", 10)) if str(payload.get("limit", "10")).isdigit() else 10)
    return {"error": "unknown", "available": ["/compose", "/history"]}


def coherence_vitals() -> dict:
    return {"layer": "generative", "status": "active", "wave": "416",
            "composer": "resonance"}


def resonates_with() -> list:
    return ["echoic_ember", "dream_weaver", "organism_genome",
            "threadweaver", "signal_loom"]
