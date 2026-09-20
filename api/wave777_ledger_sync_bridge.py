"""Wave 777 — ledger_sync_bridge.

Ingest sibling IXPANSION-LEDGER.json shapes (issuer, stones, neighbors)
into a local organ index — offline-first; optional live fetch later.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave777_ledger_sync_bridge.json"
WAVE = 777
NAME = "ledger_sync_bridge"
MAX_ENTRIES = 48

SEED_NEIGHBORS = [
    "astral-forge", "chronocrypt-orrery", "echotide-engine", "interstice",
    "luminant-reliquary", "nexus-observatory", "polychron-atlas", "solid-organism",
    "antimemetic-architecton", "phaseshift-manifold", "oracle-engine",
]

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "entries": [],
    "syncs": 0,
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


def _normalize(ledger: dict) -> dict:
    return {
        "issuer": str(ledger.get("issuer") or ledger.get("repo") or "unknown")[:64],
        "repo": str(ledger.get("repo") or "")[:64],
        "ledger_wave": ledger.get("wave"),
        "stones": list(ledger.get("stones") or [])[:16],
        "neighbors": list(ledger.get("neighbors") or [])[:64],
        "seal": str(ledger.get("seal") or "")[:32],
        "ts": _now(),
    }


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave777_ledger_sync_bridge",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "syncs": int(st.get("syncs") or 0),
        "entries": len(st.get("entries") or []),
        "resonance": round(min(1.0, 0.5 + int(st.get("syncs") or 0) * 0.01), 4),
        "surface": "silence",
        "mode": "offline_first",
    }


def resonates_with() -> list:
    return [
        "wave775_constellation_affinity",
        "wave774_wave_gap_healer",
        "wave773_ci_sentinel_bridge",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "seed_neighbors": SEED_NEIGHBORS[:8],
            "audio": False,
            "surface": "silence",
        }

    if action == "ingest":
        ledger = req.get("ledger")
        if not isinstance(ledger, dict):
            ledger = {
                "issuer": "ixpansion",
                "repo": str(req.get("repo") or "ixpansion"),
                "wave": WAVE,
                "stones": [f"LOCAL-{WAVE}"],
                "neighbors": SEED_NEIGHBORS,
                "seal": "offline",
            }
        entry = _normalize(ledger)
        entries = [e for e in list(st.get("entries") or []) if e.get("repo") != entry["repo"]]
        entries.append(entry)
        st["entries"] = entries[-MAX_ENTRIES:]
        st["syncs"] = int(st.get("syncs") or 0) + 1
        st["status"] = "synced"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "synced",
            "entry": {k: entry[k] for k in ("issuer", "repo", "ledger_wave", "seal") if k in entry},
            "neighbor_count": len(entry.get("neighbors") or []),
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "index":
        entries = st.get("entries") or []
        return {
            **coherence_vitals(),
            "status": "indexed",
            "repos": [e.get("repo") for e in entries],
            "count": len(entries),
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("syncs") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"ledgers synced {n} · entries {len(st.get('entries') or [])}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "ingest"}), indent=2))
