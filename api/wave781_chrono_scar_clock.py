"""Wave 781 — chrono_scar_clock.

Chronocrypt-inspired gyre: tick budgets for lab CI/soak isolation.
Each scar is a bounded time slice; plasma work must fit a scar or abort.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave781_chrono_scar_clock.json"
WAVE = 781
NAME = "chrono_scar_clock"
DEFAULT_BUDGET_MS = 5000
MAX_SCARS = 32

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "scars": [],
    "ticks": 0,
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
        "module": "wave781_chrono_scar_clock",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "ticks": int(st.get("ticks") or 0),
        "scars": len(st.get("scars") or []),
        "resonance": round(min(1.0, 0.5 + int(st.get("ticks") or 0) * 0.008), 4),
        "surface": "silence",
        "default_budget_ms": DEFAULT_BUDGET_MS,
    }


def resonates_with() -> list:
    return [
        "wave779_phaseshift_router",
        "wave773_ci_sentinel_bridge",
        "wave776_merge_readiness_score",
        "wave772_afterimage_well",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "open":
        try:
            budget = int(req.get("budget_ms") or DEFAULT_BUDGET_MS)
        except (TypeError, ValueError):
            budget = DEFAULT_BUDGET_MS
        budget = max(50, min(120_000, budget))
        label = str(req.get("label") or "scar")[:40]
        scar = {
            "id": f"scar-{int(st.get('ticks') or 0) + 1}",
            "label": label,
            "budget_ms": budget,
            "opened_at": _now(),
            "opened_mono": time.monotonic(),
            "closed": False,
        }
        scars = list(st.get("scars") or [])
        scars.append(scar)
        st["scars"] = scars[-MAX_SCARS:]
        st["ticks"] = int(st.get("ticks") or 0) + 1
        st["status"] = "open"
        st["active_id"] = scar["id"]
        _save(st)
        return {
            **coherence_vitals(),
            "status": "opened",
            "scar": {"id": scar["id"], "label": label, "budget_ms": budget},
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "close":
        sid = str(req.get("id") or st.get("active_id") or "")
        scars = list(st.get("scars") or [])
        found = None
        for s in reversed(scars):
            if s.get("id") == sid or (not sid and not s.get("closed")):
                found = s
                break
        if not found:
            return {**coherence_vitals(), "status": "no_scar", "audio": False}
        elapsed = 0.0
        if "opened_mono" in found:
            elapsed = (time.monotonic() - float(found["opened_mono"])) * 1000
        budget = int(found.get("budget_ms") or DEFAULT_BUDGET_MS)
        within = elapsed <= budget
        found["closed"] = True
        found["elapsed_ms"] = round(elapsed, 2)
        found["within_budget"] = within
        st["scars"] = scars
        st["status"] = "closed"
        st["last_within"] = within
        _save(st)
        return {
            **coherence_vitals(),
            "status": "closed",
            "id": found.get("id"),
            "elapsed_ms": found["elapsed_ms"],
            "budget_ms": budget,
            "within_budget": within,
            "advice": "ok" if within else "abort_or_split_plasma",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("ticks") or 0)
        w = st.get("last_within")
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"chrono scars {n}" + (f" · last {'ok' if w else 'over'}" if w is not None else ""),
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "open", "label": "demo", "budget_ms": 100}), indent=2))
