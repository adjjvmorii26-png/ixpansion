"""Wave 775 — constellation_affinity.

Experimental: map sibling consciousness-lineage repos into a soft affinity
graph (theme-folded SHA hypervectors + Hamming affinity). Catalog embedded.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave775_constellation_affinity.json"
WAVE = 775
NAME = "constellation_affinity"
DIM = 64

CONSTELLATION = [
    {"id": "ixpansion", "themes": ["aleph", "wave", "council", "vsa", "mesh"]},
    {"id": "luminant-reliquary", "themes": ["crystal", "shatter", "ember", "prism", "memory"]},
    {"id": "polychron-atlas", "themes": ["time", "paradox", "glyph", "atlas", "echo"]},
    {"id": "chronocrypt-orrery", "themes": ["cycle", "meridian", "fracture", "archive", "choir"]},
    {"id": "echotide-engine", "themes": ["tide", "wave", "reef", "abyss", "crest"]},
    {"id": "astral-forge", "themes": ["lattice", "forge", "agent", "crystal", "seraph"]},
    {"id": "antimemetic-architecton", "themes": ["absence", "erasure", "null", "inversion", "void"]},
    {"id": "phaseshift-manifold", "themes": ["phase", "solid", "liquid", "plasma", "condensate"]},
    {"id": "nexus-observatory", "themes": ["meta", "interop", "resonance", "consensus", "mesh"]},
    {"id": "pentaxis-5d-engine", "themes": ["5d", "projection", "space", "mind", "meta"]},
    {"id": "oracle-engine", "themes": ["research", "consensus", "perspective", "synthesis"]},
    {"id": "solid-organism", "themes": ["pulse", "phoenix", "omega", "lattice", "health"]},
    {"id": "interstice", "themes": ["between", "html", "portal"]},
    {"id": "collaborative-canvas", "themes": ["co-create", "canvas", "human", "ai"]},
]

DEFAULT = {"wave": WAVE, "name": NAME, "maps": 0, "status": "idle"}


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


def _hv(text: str) -> bytes:
    h = hashlib.sha512(text.encode("utf-8")).digest()
    out = bytearray(DIM)
    for i, b in enumerate(h):
        out[i % DIM] ^= b
    return bytes(out)


def _hamming(a: bytes, b: bytes) -> int:
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b))


def _affinity(a: bytes, b: bytes) -> float:
    bits = DIM * 8
    return round(1.0 - (_hamming(a, b) / bits), 4)


def _node_vec(node: dict) -> bytes:
    blob = node["id"] + "|" + "|".join(sorted(node.get("themes") or []))
    return _hv(blob)


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave775_constellation_affinity",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "maps": int(st.get("maps") or 0),
        "catalog_size": len(CONSTELLATION),
        "resonance": round(min(1.0, 0.48 + int(st.get("maps") or 0) * 0.01), 4),
        "surface": "silence",
        "dim_bits": DIM * 8,
    }


def resonates_with() -> list:
    return [
        "wave774_wave_gap_healer",
        "wave769_void_index",
        "wave767_mycelial_truths",
        "wave773_ci_sentinel_bridge",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "repos": [c["id"] for c in CONSTELLATION],
            "audio": False,
            "surface": "silence",
        }

    if action == "map":
        seed = str(req.get("seed") or "ixpansion")
        nodes = {c["id"]: _node_vec(c) for c in CONSTELLATION}
        if seed not in nodes:
            nodes[seed] = _hv(seed)
        seed_v = nodes[seed]
        ranked = sorted(
            ({"id": cid, "affinity": _affinity(seed_v, vec)} for cid, vec in nodes.items() if cid != seed),
            key=lambda x: -x["affinity"],
        )
        st["maps"] = int(st.get("maps") or 0) + 1
        st["status"] = "mapped"
        st["last_seed"] = seed
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "mapped",
            "seed": seed,
            "top": ranked[:8],
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "pair":
        a = str(req.get("a") or "ixpansion")
        b = str(req.get("b") or "nexus-observatory")
        va = next((_node_vec(c) for c in CONSTELLATION if c["id"] == a), _hv(a))
        vb = next((_node_vec(c) for c in CONSTELLATION if c["id"] == b), _hv(b))
        return {
            **coherence_vitals(),
            "status": "paired",
            "a": a,
            "b": b,
            "affinity": _affinity(va, vb),
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("maps") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"constellation maps {n} · {len(CONSTELLATION)} stars",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "map", "seed": "ixpansion"}), indent=2))
