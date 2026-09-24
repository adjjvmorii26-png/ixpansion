"""Wave 822 — gate_priority.

Dual-track doctrine as an organ: organism gates (gate, council-smoke,
boot, smoke, graft, lint) outrank full ALEPH test matrix and GHAS noise.
Silence is the product surface.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave822_gate_priority.json"
WAVE = 822
NAME = "gate_priority"

ORGANISM_GATES = (
    "gate",
    "council-smoke",
    "boot",
    "smoke",
    "graft",
    "lint",
)

NOISE_CHECKS = (
    "test",
    "github-advanced-security",
    "ghas",
)

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "rulings": 0,
    "last_ruling": None,
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


def _rule(checks: dict) -> dict:
    """Decide merge_ok from organism gates vs noise."""
    labs = {k: bool(checks.get(k, False)) for k in ORGANISM_GATES}
    lab_ok = all(labs.values()) if labs else False
    noise_red = any(bool(checks.get(k, False)) for k in NOISE_CHECKS)
    merge_ok = lab_ok
    token = "merge" if merge_ok else "hold"
    if merge_ok and noise_red:
        token = "merge_over_noise"
    return {
        "lab_ok": lab_ok,
        "noise_red": noise_red,
        "merge_ok": merge_ok,
        "token": token,
        "surface": "silence",
    }


def coherence_vitals() -> dict:
    st = _load()
    rulings = int(st.get("rulings") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave822_gate_priority",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "rulings": rulings,
        "last_ruling": st.get("last_ruling"),
        "resonance": round(min(1.0, 0.53 + rulings * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave821_still_interval",
        "wave816_ci_gate_mirror",
        "wave820_observatory_pulse",
        "wave799_hold_seam",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "rule":
        checks = req.get("checks") or {}
        if not isinstance(checks, dict):
            checks = {}
        ruling = _rule(checks)
        ruling["ts"] = _now()
        st["rulings"] = int(st.get("rulings") or 0) + 1
        st["last_ruling"] = ruling
        st["status"] = "ruled"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "ruled",
            "ruling": ruling,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("rulings") or 0)
        tok = (st.get("last_ruling") or {}).get("token")
        line = f"gate priority ×{n}" + (f" · {tok}" if tok else "")
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": line,
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(
        json.dumps(
            handler(
                {
                    "action": "rule",
                    "checks": {
                        "gate": True,
                        "council-smoke": True,
                        "boot": True,
                        "smoke": True,
                        "graft": True,
                        "lint": True,
                        "test": True,
                        "ghas": True,
                    },
                }
            ),
            indent=2,
        )
    )
