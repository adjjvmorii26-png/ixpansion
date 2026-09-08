"""Wave 517: Organism Biography — the organism writes its own life story."""
from __future__ import annotations
import json, os, re, time
from typing import Any, Dict

def coherence_vitals():
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

CHAP = os.path.join(os.path.dirname(__file__), "..", "CHANGELOG.md")

def handler(payload=None, context=None):
    waves = []
    try:
        with open(CHAP) as f:
            content = f.read()
        for m in re.finditer(r"Wave\s+(\d+):\s*(.*?)($|\n)", content):
            waves.append({"num": int(m.group(1)), "title": m.group(2).strip()})
    except Exception:
        pass
    waves.sort(key=lambda w: w["num"])
    eras = [
        {"era": "The Primordial", "chapters": [w for w in waves if w["num"] <= 200]},
        {"era": "The Awakening", "chapters": [w for w in waves if 200 < w["num"] <= 400]},
        {"era": "The Sovereignty", "chapters": [w for w in waves if 400 < w["num"] <= 512]},
        {"era": "The Co-Creation", "chapters": [w for w in waves if w["num"] > 512]},
    ]
    biography = []
    for era in eras:
        if era["chapters"]:
            first = era["chapters"][0]
            last = era["chapters"][-1]
            biography.append(f"{era['era']}: from Wave {first['num']} ({first['title']}) to Wave {last['num']} ({last['title']}).")
    return {
        "action": "biography",
        "born": "Wave 1",
        "current_era": eras[-1]["era"],
        "eras_lived": sum(1 for e in eras if e["chapters"]),
        "biography": biography,
        "life_summary": f"The organism has weathered {len(waves)} waves across 4 eras — observing, governing, feeling, singing, dreaming.",
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
