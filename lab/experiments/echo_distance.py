#!/usr/bin/env python3
"""Echo Distance — Hamming distance between two file digests."""
from __future__ import annotations
import json, hashlib, sys
from datetime import datetime, timezone
from pathlib import Path
def digest(p: Path) -> bytes:
    if not p.exists():
        return hashlib.sha256(b"missing").digest()
    return hashlib.sha256(p.read_bytes()[:65536]).digest()
def hamming(a: bytes, b: bytes) -> int:
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b))
def main():
    repo = Path(__file__).resolve().parents[2]
    pa = Path(sys.argv[1]) if len(sys.argv) > 1 else repo / "lab" / "CHRONOFORGE" / "runtime" / "cf_portal.py"
    pb = Path(sys.argv[2]) if len(sys.argv) > 2 else repo / "lab" / "experiments" / "carnival.py"
    if not pa.is_absolute(): pa = repo / pa
    if not pb.is_absolute(): pb = repo / pb
    d = hamming(digest(pa), digest(pb))
    frames = [{"t": "0.0s", "role": "hook", "text": "ECHO DISTANCE", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"hamming {d}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"{pa.name} ↔ {pb.name}", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · measure the gap", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "echo_distance", "a": str(pa), "b": str(pb), "hamming": d, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
