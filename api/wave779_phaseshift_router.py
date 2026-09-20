"""Wave 779 — phaseshift_router.

Route lab work by matter-phase metaphor (phaseshift-manifold):
  solid  — deterministic / compile / contract checks
  liquid — stateful memory / ledger sync
  gas    — exploratory / low-cost probes
  plasma — high-energy / soak / chaos

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave779_phaseshift_router.json"
WAVE = 779
NAME = "phaseshift_router"
PHASES = ("solid", "liquid", "gas", "plasma")

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "routes": 0,
    "last_phase": None,
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


def _classify(hint: str, load: float) -> str:
    h = (hint or "").lower()
    if any(k in h for k in ("chaos", "soak", "stress", "plasma")):
        return "plasma"
    if any(k in h for k in ("probe", "explore", "draft", "gas")):
        return "gas"
    if any(k in h for k in ("ledger", "memory", "state", "liquid")):
        return "liquid"
    if any(k in h for k in ("test", "compile", "contract", "gate", "solid")):
        return "solid"
    if load >= 0.85:
        return "plasma"
    if load >= 0.55:
        return "liquid"
    if load >= 0.25:
        return "gas"
    return "solid"


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave779_phaseshift_router",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "routes": int(st.get("routes") or 0),
        "last_phase": st.get("last_phase"),
        "phases": list(PHASES),
        "resonance": round(min(1.0, 0.5 + int(st.get("routes") or 0) * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave776_merge_readiness_score",
        "wave773_ci_sentinel_bridge",
        "wave777_ledger_sync_bridge",
        "wave770_copilot_council_pulse",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "route":
        hint = str(req.get("hint") or req.get("task") or "")
        try:
            load = float(req.get("load") if req.get("load") is not None else 0.3)
        except (TypeError, ValueError):
            load = 0.3
        load = max(0.0, min(1.0, load))
        phase = _classify(hint, load)
        advice = {
            "solid": "Run contract/tests; path-filtered lab CI",
            "liquid": "Prefer ledger/state organs; short persistence",
            "gas": "Cheap probe; no soak; caption-only side effects",
            "plasma": "Isolate chaos/soak; timeout hard; dual-track only",
        }[phase]
        st["routes"] = int(st.get("routes") or 0) + 1
        st["last_phase"] = phase
        st["status"] = "routed"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "routed",
            "phase": phase,
            "load": load,
            "advice": advice,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        p = st.get("last_phase") or "unset"
        n = int(st.get("routes") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"phase {p} · routes {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "route", "hint": "lab probe", "load": 0.2}), indent=2))
