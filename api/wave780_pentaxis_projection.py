"""Wave 780 — pentaxis_projection.

Project 5D intent axes (Σ space, Τ time, Ψ state, Μ mind, Ω meta)
into 2D dashboard coordinates — bridge to pentaxis-5d-engine metaphor.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave780_pentaxis_projection.json"
WAVE = 780
NAME = "pentaxis_projection"
AXES = ("sigma", "tau", "psi", "mu", "omega")

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "projections": 0,
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


def _clamp01(v) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        x = 0.5
    return max(0.0, min(1.0, x))


def _project(vec: dict) -> dict:
    s = _clamp01(vec.get("sigma", vec.get("S", 0.5)))
    t = _clamp01(vec.get("tau", vec.get("T", 0.5)))
    p = _clamp01(vec.get("psi", vec.get("P", 0.5)))
    m = _clamp01(vec.get("mu", vec.get("M", 0.5)))
    o = _clamp01(vec.get("omega", vec.get("O", 0.5)))
    x = round((s * 0.6 + m * 0.4) * 1000) / 1000
    y = round((t * 0.55 + p * 0.45) * 1000) / 1000
    energy = round(math.sqrt(s * s + t * t + p * p + m * m + o * o) / math.sqrt(5), 4)
    return {
        "x": x,
        "y": y,
        "omega": o,
        "energy": energy,
        "axes": {"sigma": s, "tau": t, "psi": p, "mu": m, "omega": o},
    }


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave780_pentaxis_projection",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "projections": int(st.get("projections") or 0),
        "axes": list(AXES),
        "resonance": round(min(1.0, 0.48 + int(st.get("projections") or 0) * 0.01), 4),
        "surface": "silence",
        "formula": "P(Σ,Τ,Ψ,Μ,Ω)→R²",
    }


def resonates_with() -> list:
    return [
        "wave775_constellation_affinity",
        "wave779_phaseshift_router",
        "wave770_copilot_council_pulse",
        "wave772_afterimage_well",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "project":
        vec = req.get("axes") if isinstance(req.get("axes"), dict) else req
        out = _project(vec if isinstance(vec, dict) else {})
        st["projections"] = int(st.get("projections") or 0) + 1
        st["status"] = "projected"
        st["last"] = {"x": out["x"], "y": out["y"], "energy": out["energy"]}
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "projected",
            **out,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("projections") or 0)
        last = st.get("last") or {}
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"pentaxis n={n} · x={last.get('x', '-')} y={last.get('y', '-')}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "project", "sigma": 0.8, "tau": 0.2, "psi": 0.5, "mu": 0.7, "omega": 0.3}), indent=2))
