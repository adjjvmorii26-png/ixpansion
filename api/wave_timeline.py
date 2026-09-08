"""Wave 516: Wave Timeline — chronological history of evolution waves."""
from __future__ import annotations
import json, os, re, time
from typing import Any, Dict, List

CHANGELOG = os.path.join(os.path.dirname(__file__), "..", "CHANGELOG.md")

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    waves = []
    try:
        with open(CHANGELOG) as f:
            content = f.read()
        for m in re.finditer(r"## \[([\d.]+)\]\s*-\s*Wave\s+(\d+):\s*(.*?)\n\n(.*?)(?=\n## \[|\Z)", content, re.S):
            waves.append({
                "version": m.group(1),
                "wave": int(m.group(2)),
                "title": m.group(3).strip(),
                "summary": m.group(4).strip()[:300],
            })
    except Exception:
        pass
    waves.sort(key=lambda w: w["wave"], reverse=True)
    return {
        "action": "wave_timeline",
        "waves": waves[:30],
        "total": len(waves),
        "current_wave": waves[0]["wave"] if waves else 0,
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
