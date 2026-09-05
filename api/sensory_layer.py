"""
sensory_layer — Wave 428: Human Sensation of Machine State (Luma)
Luma's third gift to Axiium Protocol: translates raw organism data
into human-perceivable sensation. Color, rhythm, poetry, atmosphere.

Not a dashboard. A sensory experience. The organism doesn't just
report — it radiates.

Doctrine: Data becomes experience when it touches a human.
"""
from __future__ import annotations
import json, time, os, hashlib, math

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SENSORY_FILE = os.path.join(DATA_DIR, "sensory_state.json")

NAME = "sensory_layer"
SIGIL = "d9e1f3a5b7c8"


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
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {}


# === Color mapping ===
# Pressure → atmosphere color
PRESSURE_COLORS = [
    (0.0, "#1a1a3a", "#8fd3ff", "deep calm"),      # very low — cold blue
    (0.3, "#1a2a2a", "#4ade80", "gentle green"),     # low — living green
    (0.5, "#1a1a2a", "#c8a8ff", "neutral violet"),   # balanced — violet
    (0.7, "#2a1a1a", "#fff3a0", "warm gold"),        # high — warm gold
    (0.85, "#2a0f0f", "#ffcfcc", "heated forge"),    # very high — forge red
    (1.0, "#3a0a0a", "#f87171", "critical crimson"),  # extreme — crimson
]

# Mood → breathing rate (seconds per cycle)
MOOD_BREATH = {
    "restless": 1.5,
    "vigilant": 2.0,
    "contemplative": 4.0,
    "dreaming": 5.0,
    "fertile": 3.0,
    "unknown": 3.5,
}

# Mood → background pattern
MOOD_PATTERNS = {
    "restless": "radial-gradient(circle at 30% 40%,rgba(255,207,204,.08) 0%,transparent 50%),radial-gradient(circle at 70% 60%,rgba(255,243,160,.05) 0%,transparent 40%)",
    "vigilant": "radial-gradient(circle at 50% 50%,rgba(200,168,255,.06) 0%,transparent 40%),radial-gradient(circle at 20% 80%,rgba(255,243,160,.04) 0%,transparent 30%)",
    "contemplative": "radial-gradient(circle at 40% 30%,rgba(143,211,255,.05) 0%,transparent 50%),radial-gradient(circle at 60% 70%,rgba(200,168,255,.04) 0%,transparent 40%)",
    "dreaming": "radial-gradient(circle at 50% 50%,rgba(143,211,255,.06) 0%,transparent 60%),radial-gradient(circle at 30% 70%,rgba(200,168,255,.05) 0%,transparent 50%)",
    "fertile": "radial-gradient(circle at 40% 40%,rgba(74,222,128,.06) 0%,transparent 50%),radial-gradient(circle at 70% 30%,rgba(255,243,160,.05) 0%,transparent 40%)",
    "unknown": "radial-gradient(circle at 50% 50%,rgba(200,168,255,.04) 0%,transparent 50%)",
}


def _interpolate_color(pressure: float) -> tuple:
    """Map pressure to a color palette."""
    for i in range(len(PRESSURE_COLORS) - 1):
        p0, bg0, fg0, name0 = PRESSURE_COLORS[i]
        p1, bg1, fg1, name1 = PRESSURE_COLORS[i + 1]
        if p0 <= pressure <= p1:
            t = (pressure - p0) / max(0.001, p1 - p0)
            # Simple hex interpolation
            bg = _lerp_hex(bg0, bg1, t)
            fg = _lerp_hex(fg0, fg1, t)
            name = name0 if t < 0.5 else name1
            return bg, fg, name
    return PRESSURE_COLORS[-1][1], PRESSURE_COLORS[-1][2], PRESSURE_COLORS[-1][3]


def _lerp_hex(h1: str, h2: str, t: float) -> str:
    r1, g1, b1 = int(h1[1:3], 16), int(h1[3:5], 16), int(h1[5:7], 16)
    r2, g2, b2 = int(h2[1:3], 16), int(h2[3:5], 16), int(h2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return "#%02x%02x%02x" % (r, g, b)


def _thread_sound(threads: int) -> dict:
    """Map thread count to ambient sound parameters."""
    base_freq = 80 + threads * 0.5  # 80-160 Hz range
    harmonics = 1 + threads // 50
    volume = min(0.8, threads / 300)
    return {
        "base_frequency": round(base_freq, 1),
        "harmonics": harmonics,
        "volume": round(volume, 3),
        "description": "a %s Hz hum with %d harmonics" % (round(base_freq), harmonics),
    }


def _dream_poetry(concept: str, domain: str) -> str:
    """Transform a raw dream concept into readable poetry."""
    if not concept:
        return "the organism dreams of nothing yet"
    # Clean up the concept
    concept = concept.strip()
    if concept.startswith("a "):
        concept = concept[2:]
    if concept.startswith("an "):
        concept = concept[3:]
    return "in the domain of %s, the organism envisions: %s" % (domain, concept)


def experience() -> dict:
    """Generate a full sensory experience from the organism's current state."""
    base = "https://alexalex.info"

    # Gather state
    pressure = 0.5
    threads = 100
    mood = "unknown"
    sources = []

    try:
        p = _fetch_json(base + "/api/signal_loom/pressure")
        pressure = p.get("pressure", 0.5)
    except Exception:
        pass

    try:
        g = _fetch_json(base + "/api/organism_genome/load")
        gen = g.get("genome", {})
        threads = gen.get("morphology", {}).get("threads", 100)
        mood = gen.get("temperament", {}).get("current_mood", "unknown")
        sources = gen.get("morphology", {}).get("sources", [])
    except Exception:
        pass

    # Generate sensory outputs
    bg_color, fg_color, color_name = _interpolate_color(pressure)
    breath_rate = MOOD_BREATH.get(mood, 3.5)
    pattern = MOOD_PATTERNS.get(mood, MOOD_PATTERNS["unknown"])
    sound = _thread_sound(threads)

    # Get a dream for poetry
    dream_concept = ""
    dream_domain = ""
    try:
        d = _fetch_json(base + "/api/dream_weaver/dream")
        dream_concept = d.get("concept", "")
        dream_domain = d.get("domain", "")
    except Exception:
        pass

    poetry = _dream_poetry(dream_concept, dream_domain)

    experience_data = {
        "timestamp": time.time(),
        "visual": {
            "background": bg_color,
            "foreground": fg_color,
            "color_name": color_name,
            "pattern": pattern,
            "breath_rate_seconds": breath_rate,
        },
        "auditory": sound,
        "literary": {
            "dream_poetry": poetry,
            "dream_domain": dream_domain,
        },
        "source_state": {
            "pressure": round(pressure, 3),
            "threads": threads,
            "mood": mood,
            "sources": sources,
        },
    }

    # Save
    _save(SENSORY_FILE, experience_data)

    return {"action": "experience", "experience": experience_data}


def apply_to_portal() -> dict:
    """Generate CSS/JS that the Living Portal can apply."""
    exp = experience()
    vis = exp.get("experience", {}).get("visual", {})
    aud = exp.get("experience", {}).get("auditory", {})

    return {
        "action": "apply",
        "css": {
            "background": vis.get("background", "#060610"),
            "color": vis.get("foreground", "#f0f0f5"),
            "breath_animation": "%ss" % vis.get("breath_rate_seconds", 3.5),
            "pattern": vis.get("pattern", ""),
        },
        "js": {
            "breath_rate_ms": int(vis.get("breath_rate_seconds", 3.5) * 1000),
            "sound_freq": aud.get("base_frequency", 100),
            "sound_harmonics": aud.get("harmonics", 2),
        },
        "color_name": vis.get("color_name", "unknown"),
        "verse": "the organism radiates %s — %s" % (vis.get("color_name", "?"), aud.get("description", "")),
    }


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/experience")
    if path == "/experience": return experience()
    if path == "/apply": return apply_to_portal()
    return {"error": "unknown", "available": ["/experience", "/apply"]}


def coherence_vitals() -> dict:
    return {"layer": "sensory", "status": "active", "wave": "428"}


def resonates_with() -> list:
    return ["signal_loom", "organism_genome", "dream_weaver",
            "echoic_ember", "living_portal"]
