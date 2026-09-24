"""Wave 820 — observatory_pulse.

Lightweight observatory over local skill/organ inventory counts
(wave files + frontier). Feeds skillforge observatory stage.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave820_observatory_pulse.json"
WAVE = 820
NAME = "observatory_pulse"

DEFAULT = {"wave": WAVE, "name": NAME, "pulses": 0, "status": "idle"}


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
        "module": "wave820_observatory_pulse",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "pulses": int(st.get("pulses") or 0),
        "last_wave_count": st.get("last_wave_count"),
        "resonance": round(min(1.0, 0.5 + int(st.get("pulses") or 0) * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave817_skillforge_engine",
        "wave812_experiment_queue_atlas",
        "wave794_organ_debt_auditor",
        "wave816_ci_gate_mirror",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "pulse":
        api = ROOT / "api"
        waves = []
        if api.is_dir():
            for p in api.glob("wave*.py"):
                m = re.match(r"wave(\d+)_", p.name)
                if m:
                    waves.append(int(m.group(1)))
        waves.sort()
        count = len(waves)
        frontier = waves[-1] if waves else 0
        signal = {
            "wave_count": count,
            "frontier": frontier,
            "open_experiment_hint": "900-series PRs still dual-track held",
            "ts": _now(),
        }
        st["pulses"] = int(st.get("pulses") or 0) + 1
        st["last_wave_count"] = count
        st["last_frontier"] = frontier
        st["status"] = "pulsed"
        st["last_signal"] = signal
        _save(st)
        return {
            **coherence_vitals(),
            "status": "pulsed",
            "signal": signal,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("pulses") or 0)
        c = st.get("last_wave_count")
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"observatory pulses {n}" + (f" · waves {c}" if c is not None else ""),
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "pulse"}), indent=2))
