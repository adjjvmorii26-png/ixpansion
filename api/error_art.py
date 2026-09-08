"""Wave 517: Error Art — turn error logs into procedural visual art descriptions."""
from __future__ import annotations
import hashlib, json, os, random, time
from typing import Any, Dict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def coherence_vitals():
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

COLORS = ["#41b3a3", "#8fd3ff", "#e8a87c", "#c38d9e", "#ffd700", "#ff6699", "#8f7fff", "#0a0a14"]
SHAPES = ["circle", "line", "arc", "spiral", "hexagon", "wave", "fractal", "void"]

def handler(payload=None, context=None):
    errors = []
    if os.path.isdir(DATA_DIR):
        for fname in os.listdir(DATA_DIR):
            if "error" in fname or "fail" in fname:
                if fname.endswith(".json"):
                    errors.append(fname.replace(".json", ""))
    rng = random.Random(time.time())
    canvas = []
    for i in range(min(20, len(errors) * 3 or 12)):
        seed_str = errors[i % len(errors)] if errors else f"empty_{i}"
        h = hashlib.sha256(seed_str.encode()).hexdigest()
        canvas.append({
            "element": i + 1,
            "shape": rng.choice(SHAPES),
            "color": COLORS[int(h[0], 16) % len(COLORS)],
            "position": {"x": int(h[2:4], 16) / 2.55, "y": int(h[4:6], 16) / 2.55},
            "rotation": int(h[6:8], 16),
            "scale": round(0.5 + int(h[8:10], 16) / 510, 2),
            "title": seed_str[:40],
        })
    return {
        "action": "error_art",
        "canvas_size": {"width": 100, "height": 100},
        "elements": canvas,
        "medium": "error prose on digital canvas",
        "artist": "the organism's shadow",
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
