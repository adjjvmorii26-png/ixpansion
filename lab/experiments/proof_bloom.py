#!/usr/bin/env python3
"""Proof Bloom — caption hash bloom for novelty."""
from __future__ import annotations
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
CAP = REPO / "content_output" / "captions"
M, K = 256, 3
def bits(s: str):
    out = set()
    for i in range(K):
        h = hashlib.sha256(f"{i}:{s}".encode()).digest()
        out.add(int.from_bytes(h[:2], "big") % M)
    return out
def main():
    filter_bits, seen, novel, samples = set(), 0, 0, []
    if CAP.exists():
        for f in sorted(CAP.glob("*.json"))[-40:]:
            try: raw = f.read_text()
            except OSError: continue
            b = bits(raw[:500])
            if b.issubset(filter_bits): seen += 1
            else: novel += 1; samples.append(f.name)
            filter_bits |= b
    frames = [{"t": "0.0s", "role": "hook", "text": "PROOF BLOOM", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"novel {novel} · echo {seen}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": (samples[-1] if samples else "empty")[:40], "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · prefer the novel bloom", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "proof_bloom", "novel": novel, "echo": seen, "bits": len(filter_bits), "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
