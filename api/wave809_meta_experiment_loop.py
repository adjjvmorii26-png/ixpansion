"""Wave 809 — meta_experiment_loop.

IXPANSION → experiment system → experiments → results
  → learn about system → learn about the experiment system → repeat

Meta-layer above discovery_cycle_engine (808): learns how experiments
themselves should change.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave809_meta_experiment_loop.json"
WAVE = 809
NAME = "meta_experiment_loop"

LAYERS = (
    "ixpansion",
    "experiment_system",
    "experiments",
    "results",
    "learn_system",
    "learn_experiment_system",
)

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "layer": "ixpansion",
    "loops": 0,
    "insights": [],
    "status": "idle",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            raw = json.loads(STATE_FILE.read_text())
            if isinstance(raw, dict):
                return raw
        except Exception:
            pass
    return dict(DEFAULT)


def _save(st: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try:
            STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError:
            pass


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave809_meta_experiment_loop",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "meta_layer": st.get("layer", "ixpansion"),
        "loops": int(st.get("loops") or 0),
        "insight_count": len(st.get("insights") or []),
        "resonance": round(
            min(1.0, 0.5 + int(st.get("loops") or 0) * 0.02 + len(st.get("insights") or []) * 0.01),
            4,
        ),
        "surface": "silence",
        "layers": list(LAYERS),
    }


def resonates_with() -> list:
    return [
        "wave808_discovery_cycle_engine",
        "wave783_hitl_publish_gate",
        "wave770_copilot_council_pulse",
        "wave794_organ_debt_auditor",
    ]


def _next(layer: str) -> str:
    if layer not in LAYERS:
        return "ixpansion"
    i = LAYERS.index(layer)
    return LAYERS[(i + 1) % len(LAYERS)]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "diagram":
        lines = [
            "IXPANSION",
            "  │",
            "  ▼",
            "EXPERIMENT SYSTEM",
            "  │",
            "  ▼",
            "EXPERIMENTS",
            "  │",
            "  ▼",
            "RESULTS",
            "  │",
            "  ▼",
            "LEARN ABOUT SYSTEM",
            "  │",
            "  ▼",
            "LEARN ABOUT THE EXPERIMENT SYSTEM",
            "  │",
            "  └──────────────► repeat",
        ]
        return {
            **coherence_vitals(),
            "status": "diagram",
            "diagram": lines,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "advance":
        note = str(req.get("note") or "")[:160]
        cur = st.get("layer") or "ixpansion"
        if cur not in LAYERS:
            cur = "ixpansion"
        nxt = _next(cur)
        st["layer"] = nxt
        st["status"] = "advanced"
        if nxt == "ixpansion" and cur == "learn_experiment_system":
            st["loops"] = int(st.get("loops") or 0) + 1
            st["status"] = "looped"
        if note:
            insights = list(st.get("insights") or [])
            insights.append({"layer": cur, "note": note, "ts": _now()})
            st["insights"] = insights[-64:]
        _save(st)
        return {
            **coherence_vitals(),
            "status": st["status"],
            "from": cur,
            "to": nxt,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "insight":
        text = str(req.get("text") or req.get("note") or "")[:200]
        if not text:
            return {
                **coherence_vitals(),
                "status": "empty_insight",
                "audio": False,
                "surface": "silence",
            }
        layer = st.get("layer") or "learn_experiment_system"
        insights = list(st.get("insights") or [])
        insights.append({"layer": layer, "note": text, "ts": _now(), "kind": "meta"})
        st["insights"] = insights[-64:]
        st["status"] = "insight_recorded"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "insight_recorded",
            "note": text,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "run_once":
        path = []
        for layer in LAYERS:
            path.append(layer)
            st["layer"] = layer
        st["loops"] = int(st.get("loops") or 0) + 1
        st["status"] = "looped"
        st["layer"] = "ixpansion"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "looped",
            "path": path,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("loops") or 0)
        layer = st.get("layer") or "ixpansion"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"meta-experiment · {layer} · loops {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "diagram"}), indent=2))
