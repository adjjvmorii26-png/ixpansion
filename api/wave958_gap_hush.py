"""Wave 958 — gap_hush.

Council Session #22 sealed five scores. The organs keep the numbers.
What sits between them is the product: four rests, compressed once.
This organ does not call 671–675. It only reads the sealed scores.

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
STATE_FILE = DATA / "wave958_gap_hush.json"
WAVE = 958
NAME = "gap_hush"

# Sealed Session #22 scores. Do not replay handlers.
SEALED = (
    {"wave": 671, "name": "harmony_braid", "persona": "AXIOME", "score": 0.761},
    {"wave": 672, "name": "root_archive", "persona": "CYTHARA", "score": 0.734},
    {"wave": 673, "name": "naming_well", "persona": "LUMINA", "score": 0.718},
    {"wave": 674, "name": "dawn_ledger", "persona": "NOOS", "score": 0.689},
    {"wave": 675, "name": "consensus_bloom", "persona": "ALEPH", "score": 0.802},
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


def score_rests() -> list:
    """Adjacent rests after sorting sealed scores. Milli-score units."""
    ordered = sorted(SEALED, key=lambda row: (row["score"], row["wave"]))
    rests = []
    for low, high in zip(ordered, ordered[1:]):
        milli = int(round((high["score"] - low["score"]) * 1000))
        rests.append({
            "low": low["wave"],
            "high": high["wave"],
            "milli": milli,
            "pair": f"{low['wave']}-{high['wave']}",
        })
    return rests


def gap_digest(rests=None) -> str:
    rests = rests if rests is not None else score_rests()
    blob = "|".join(f"{r['pair']}:{r['milli']}" for r in rests)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def coherence_vitals() -> dict:
    st = _load()
    n = int(st.get("compressions") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave958_gap_hush",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "compressions": n,
        "rests": 4,
        "resonance": round(min(1.0, 0.52 + n * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave671_harmony_braid",
        "wave672_root_archive",
        "wave673_naming_well",
        "wave674_dawn_ledger",
        "wave675_consensus_bloom",
        "wave957_absent_ledger",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "compress":
        rests = score_rests()
        digest = gap_digest(rests)
        widest = max(rests, key=lambda row: row["milli"])
        st["compressions"] = int(st.get("compressions") or 0) + 1
        st["digest"] = digest
        st["status"] = "compressed"
        st["last_ts"] = _now()
        st["span_milli"] = sum(row["milli"] for row in rests)
        st["widest"] = widest["pair"]
        _save(st)
        return {
            **coherence_vitals(),
            "status": "compressed",
            "digest": digest,
            "span_milli": st["span_milli"],
            "widest": widest["pair"],
            "caption": f"gap hush · {digest}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        digest = st.get("digest") or gap_digest()
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"session 22 rests {digest}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "compress"}), indent=2))
