#!/usr/bin/env python3
"""Quine Pulse — caption from this file's own hash."""
from __future__ import annotations
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path
def main():
    src = Path(__file__).read_bytes()
    h = hashlib.sha256(src).hexdigest()
    melody = "-".join(str(int(h[i], 16) % 8) for i in range(0, 12, 2))
    frames = [{"t": "0.0s", "role": "hook", "text": "QUINE PULSE", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"self {h[:12]}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"{len(src)}B · tone {melody}", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · the code names itself", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "quine_pulse", "self_hash": h[:16], "bytes": len(src), "melody": melody, "frames": frames, "audio": None, "doctrine": "identity is a hash of practice", "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
