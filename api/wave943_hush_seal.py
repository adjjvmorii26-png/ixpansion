"""Wave 943 — hush_seal.

Compress hush_ledger tokens into a silent seal hash. Does not re-record.
Silence is the product surface. Lab organ only.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave943_hush_seal.json"
WAVE = 943
NAME = "hush_seal"

DEFAULT = {"wave": WAVE, "name": NAME, "seal": "", "source_n": 0, "status": "idle"}


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


def _seal_of(tokens: list[str]) -> str:
    joined = "|".join(tokens) if tokens else "empty-ledger"
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def coherence_vitals() -> dict:
    st = _load()
    seal = str(st.get("seal") or "")
    n = int(st.get("source_n") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave943_hush_seal",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "seal": seal,
        "source_n": n,
        "resonance": round(min(1.0, 0.54 + (0.04 if seal else 0) + n * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave942_hush_ledger",
        "wave941_hush_fold",
        "wave938_pulse_compress",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "seal":
        tokens = req.get("tokens")
        if not isinstance(tokens, list):
            tokens = []
            try:
                ledger = _import_api("wave942_hush_ledger")
                lst = ledger._load()
                entries = lst.get("entries") or []
                tokens = [str((e or {}).get("token") or "") for e in entries if isinstance(e, dict)]
            except Exception:
                tokens = []
        tokens = [str(t)[:16] for t in tokens if str(t)]
        seal = _seal_of(tokens)
        st["seal"] = seal
        st["source_n"] = len(tokens)
        st["status"] = "sealed"
        st["ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "sealed",
            "seal": seal,
            "source_n": len(tokens),
            "caption": f"hush seal {seal} · n={len(tokens)}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        seal = st.get("seal") or "unsealed"
        n = int(st.get("source_n") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"hush seal {seal} n={n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "seal"}), indent=2))
