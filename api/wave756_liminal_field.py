"""Wave 756 — liminal_field.

A shimmering in-between layer where modules temporarily dissolve identity
and recombine into novel forms. Tracks which organs are currently in
liminal state and what emergent forms have been birthed.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave756_liminal_field.json"
WAVE = 756
NAME = "liminal_field"


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "dissolved": [], "reformed": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def _merge_names(a: str, b: str) -> str:
    parts_a = a.split("_")
    parts_b = b.split("_")
    merged = []
    for i in range(max(len(parts_a), len(parts_b))):
        if i < len(parts_a) and i < len(parts_b):
            merged.append(parts_a[i][:2] + parts_b[i][-2:])
        elif i < len(parts_a):
            merged.append(parts_a[i])
        else:
            merged.append(parts_b[i])
    return "_".join(merged)


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        dissolved = [d for d in state.get("dissolved", []) if not d.get("reformed")]
        return {"wave": WAVE, "name": NAME, "action": "status", "ok": True,
                "currently_dissolved": len(dissolved),
                "total_reformed": len(state.get("reformed", []))}

    if action == "ping":
        return {"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}

    if action == "dissolve":
        organ = req.get("organ", "unknown")
        entry = {
            "organ": organ,
            "dissolved_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "reformed": False,
        }
        state.setdefault("dissolved", []).append(entry)
        state["dissolved"] = state["dissolved"][-30:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "dissolve", "ok": True,
                "organ": organ, "total_dissolved": len(state["dissolved"])}

    if action == "reform":
        organs = req.get("organs", [])
        if len(organs) < 2:
            return {"wave": WAVE, "name": NAME, "action": "reform", "ok": False,
                    "error": "need_at_least_2_organs"}
        hybrid_name = _merge_names(organs[0], organs[1])
        hybrid = {
            "name": hybrid_name,
            "parents": organs[:2],
            "reformed_at": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        state.setdefault("reformed", []).append(hybrid)
        for d in state.get("dissolved", []):
            if d["organ"] in organs[:2] and not d["reformed"]:
                d["reformed"] = True
        state["reformed"] = state["reformed"][-20:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "reform", "ok": True,
                "hybrid": hybrid["name"], "parents": hybrid["parents"],
                "total_reformed": len(state["reformed"])}

    if action == "pulse":
        dissolved = [d for d in state.get("dissolved", []) if not d.get("reformed")]
        reformed = state.get("reformed", [])
        return {"wave": WAVE, "name": NAME, "action": "pulse", "ok": True,
                "dissolved_count": len(dissolved),
                "reformed_count": len(reformed),
                "field_strength": round(0.5 + len(dissolved) * 0.05 - len(reformed) * 0.02, 3)}

    return {"wave": WAVE, "name": NAME, "action": action, "ok": False,
            "error": "unknown_action"}


def coherence_vitals() -> dict:
    state = _load()
    dissolved = [d for d in state.get("dissolved", []) if not d.get("reformed")]
    return {"wave": WAVE, "name": NAME, "layer": "organ", "status": "active",
            "resonance": 0.68, "dissolved": len(dissolved),
            "reformed": len(state.get("reformed", []))}


def resonates_with() -> list:
    return ["threshold_engine", "resonance_braid", "gene_splicer"]
