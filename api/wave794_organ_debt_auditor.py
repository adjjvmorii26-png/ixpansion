"""Wave 794 — organ_debt_auditor.

Scan api/wave*.py for coherence_vitals + handler presence (lightweight debt).
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "api"
DATA = ROOT / "data"
STATE_FILE = DATA / "wave794_organ_debt_auditor.json"
WAVE = 794
NAME = "organ_debt_auditor"

DEFAULT = {"wave": WAVE, "name": NAME, "audits": 0, "status": "idle"}


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
        "module": "wave794_organ_debt_auditor",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "audits": int(st.get("audits") or 0),
        "last_debt": st.get("last_debt"),
        "resonance": round(min(1.0, 0.5 + int(st.get("audits") or 0) * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave776_merge_readiness_score",
        "wave787_dual_track_pr_bot",
        "wave773_ci_sentinel_bridge",
        "wave770_copilot_council_pulse",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "audit":
        missing_v = []
        missing_h = []
        scanned = 0
        if API.is_dir():
            for p in sorted(API.glob("wave*.py")):
                scanned += 1
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if "def coherence_vitals" not in text:
                    missing_v.append(p.name)
                if "def handler" not in text:
                    missing_h.append(p.name)
        debt = len(missing_v) + len(missing_h)
        st["audits"] = int(st.get("audits") or 0) + 1
        st["last_debt"] = debt
        st["status"] = "audited"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "audited",
            "scanned": scanned,
            "debt": debt,
            "missing_coherence_vitals": missing_v[:20],
            "missing_handler": missing_h[:20],
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("audits") or 0)
        d = st.get("last_debt")
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"organ debt audits {n}" + (f" · debt {d}" if d is not None else ""),
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "audit"}), indent=2))
