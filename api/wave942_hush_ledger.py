"""Wave 942 — hush_ledger.

Record the last hush_fold token into a silent ledger. Does not re-fold.
Silence is the product surface. Lab organ only.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave942_hush_ledger.json"
WAVE = 942
NAME = "hush_ledger"
MAX_ENTRIES = 16

DEFAULT = {"wave": WAVE, "name": NAME, "entries": [], "status": "idle"}


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


def _import_api(mod: str):
    api = ROOT / "api"
    if str(api) not in sys.path:
        sys.path.insert(0, str(api))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    return __import__(mod)


def coherence_vitals() -> dict:
    st = _load()
    entries = st.get("entries") or []
    n = len(entries) if isinstance(entries, list) else 0
    last = entries[-1] if n else {}
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave942_hush_ledger",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "entries": n,
        "last_token": (last or {}).get("token") or "",
        "resonance": round(min(1.0, 0.52 + n * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave941_hush_fold",
        "wave940_residual_chain_cap",
        "wave939_residual_bind",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "record":
        token = str(req.get("token") or "")
        if not token:
            try:
                fold = _import_api("wave941_hush_fold")
                f = fold.handler({"action": "status"})
                token = str(f.get("token") or "")
            except Exception:
                token = ""
        token = token or "empty-hush"
        entries = list(st.get("entries") or [])
        entries.append({"token": token[:16], "ts": _now()})
        st["entries"] = entries[-MAX_ENTRIES:]
        st["status"] = "recorded"
        st["ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "recorded",
            "token": token[:16],
            "caption": f"hush ledger {len(st['entries'])} · {token[:16]}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = len(st.get("entries") or [])
        last = (st.get("entries") or [{}])[-1] if n else {}
        tok = (last or {}).get("token") or "empty"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"hush ledger {n} last {tok}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "record"}), indent=2))
