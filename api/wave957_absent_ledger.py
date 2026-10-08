"""Wave 957 — absent_ledger.

Council Session #22 sealed five organs. Shared keys are the public face.
What each organ refuses to share is the memory. This organ does not call
671–675. It compresses the sealed absence map into one silent digest.

Silence is the product surface. Compression is memory.
Lab gate only — not ALEPH CI.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave957_absent_ledger.json"
WAVE = 957
NAME = "absent_ledger"

# Sealed Session #22 absence map. Do not replay handlers.
SEALED = (
    {"wave": 671, "name": "harmony_braid", "persona": "AXIOME", "score": 0.761,
     "only": ("strands", "braids", "debt")},
    {"wave": 672, "name": "root_archive", "persona": "CYTHARA", "score": 0.734,
     "only": ("ghosts", "echoes")},
    {"wave": 673, "name": "naming_well", "persona": "LUMINA", "score": 0.718,
     "only": ("names", "epochs")},
    {"wave": 674, "name": "dawn_ledger", "persona": "NOOS", "score": 0.689,
     "only": ("cycle", "dawns", "rhythm")},
    {"wave": 675, "name": "consensus_bloom", "persona": "ALEPH", "score": 0.802,
     "only": ("proposals", "blooms", "quorum")},
)

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "compressions": 0,
    "digest": "",
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


def absence_rows() -> list:
    """Keys present on one organ and absent from the other four."""
    rows = []
    for organ in SEALED:
        others = [o for o in SEALED if o["wave"] != organ["wave"]]
        foreign = set()
        for o in others:
            foreign.update(o["only"])
        absent = tuple(sorted(k for k in organ["only"] if k not in foreign))
        rows.append({
            "wave": organ["wave"],
            "name": organ["name"],
            "persona": organ["persona"],
            "score": organ["score"],
            "absent": absent,
        })
    return rows


def absence_digest(rows=None) -> str:
    rows = rows if rows is not None else absence_rows()
    blob = "|".join(
        f"{r['wave']}:{','.join(r['absent'])}" for r in rows
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def coherence_vitals() -> dict:
    st = _load()
    n = int(st.get("compressions") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave957_absent_ledger",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "compressions": n,
        "organs": 5,
        "resonance": round(min(1.0, 0.55 + n * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave671_harmony_braid",
        "wave672_root_archive",
        "wave673_naming_well",
        "wave674_dawn_ledger",
        "wave675_consensus_bloom",
        "wave956_rank_hush",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "compress":
        rows = absence_rows()
        digest = absence_digest(rows)
        st["compressions"] = int(st.get("compressions") or 0) + 1
        st["digest"] = digest
        st["status"] = "compressed"
        st["last_ts"] = _now()
        st["width"] = sum(len(r["absent"]) for r in rows)
        _save(st)
        return {
            **coherence_vitals(),
            "status": "compressed",
            "digest": digest,
            "width": st["width"],
            "caption": f"absent ledger · {digest}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        digest = st.get("digest") or absence_digest()
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"session 22 absence {digest}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "compress"}), indent=2))
