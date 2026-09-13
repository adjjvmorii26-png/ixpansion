#!/usr/bin/env python3
"""Compass Rose — hash a word onto proof/silence/fold/ceremony."""
from __future__ import annotations
import json, hashlib, sys
from datetime import datetime, timezone
AXES = ("proof", "silence", "fold", "ceremony")
def main():
    word = " ".join(sys.argv[1:]) or "IXPANSION"
    h = hashlib.sha256(word.encode()).digest()
    weights = {AXES[i]: round(h[i] / 255.0, 3) for i in range(4)}
    bearing = max(weights, key=weights.get)
    frames = [{"t": "0.0s", "role": "hook", "text": "COMPASS ROSE", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"bearing {bearing}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": " · ".join(f"{k}:{v}" for k, v in weights.items()), "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · face the heavy axis", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "compass_rose", "word": word, "weights": weights, "bearing": bearing, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
