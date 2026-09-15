#!/usr/bin/env python3
"""Epoch Coin — day-hash chooses EXPAND vs COMPACT ritual."""
from __future__ import annotations
import json, hashlib
from datetime import datetime, timezone
def main():
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    h = hashlib.sha256(day.encode()).hexdigest()
    face = "EXPAND" if int(h[:2], 16) % 2 == 0 else "COMPACT"
    frames = [{"t": "0.0s", "role": "hook", "text": "EPOCH COIN", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": face, "style": "magenta"}, {"t": "5.0s", "role": "live", "text": day, "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · ritual without dice", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "epoch_coin", "day": day, "face": face, "sig": h[:12], "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
