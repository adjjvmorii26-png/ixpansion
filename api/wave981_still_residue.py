#!/usr/bin/env python3
"""Wave 981 — Still Residue

Compression is memory. Silence is the product surface.
Takes a hush score (or triad) and folds it into a fixed 8-char still residue.
No audio, no payload, pure deterministic.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, Mapping


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return lo
    if v != v:
        return lo
    return max(lo, min(hi, v))


def still_residue(score: float, salt: str = "") -> str:
    """Fold hush score into 8-char residue. Higher hush → more zeros (still)."""
    s = _clamp(score)
    raw = f"{s:.6f}:{salt}".encode()
    h = hashlib.sha256(raw).hexdigest()
    # bias toward still (more 0) when score high
    zeros = int(s * 4)
    body = ("0" * zeros) + h[zeros:8]
    return body[:8]


def evaluate(metrics: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    m = metrics or {}
    if "hush_score" in m:
        score = _clamp(m["hush_score"])
    else:
        g = _clamp(m.get("gossip", 0.5))
        f = _clamp(m.get("forge", 0.5))
        t = _clamp(m.get("time", 0.5))
        pressure = (g + f + t) / 3.0
        score = round(1.0 - (pressure ** 0.85), 4)
    salt = str(m.get("salt") or m.get("id") or "")[:32]
    residue = still_residue(score, salt)
    return {
        "wave": 981,
        "organ": "still_residue",
        "doctrine": "compression is memory; silence is the product surface",
        "hush_score": score,
        "residue": residue,
        "product_surface": "hush",
        "bytes_kept": 8,
    }


def coherence_vitals() -> Dict[str, Any]:
    return {
        "wave": 981,
        "module": "wave981_still_residue",
        "ok": True,
        "persona": "HUSH",
        "residue_len": 8,
        "surface": "silence",
    }


def resonates_with() -> list[str]:
    return ["wave980_hush_tide", "wave944_hush_still", "wave942_hush_ledger"]


def handler(query: Dict[str, Any] | None = None) -> Dict[str, Any]:
    q = query or {}
    action = (q.get("action") or "evaluate").lower()
    if action == "status":
        return {"status": "active", **coherence_vitals()}
    return {"status": "residued", **evaluate(q), **coherence_vitals()}


if __name__ == "__main__":
    import json
    print(json.dumps(handler({"hush_score": 0.85}), indent=2))
