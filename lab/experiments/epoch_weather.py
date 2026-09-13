#!/usr/bin/env python3
"""Epoch Weather — CHRONOFORGE epoch → organism sky."""
from __future__ import annotations
import json, hashlib, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
PORTAL = REPO / "lab" / "CHRONOFORGE" / "runtime" / "cf_portal.py"
SKY = {"E1": "clear", "E2": "aurora", "E3": "storm", "E∞": "fog", "EINF": "fog"}
def main():
    epoch = "E1"
    if PORTAL.exists():
        r = subprocess.run([sys.executable, str(PORTAL), "epoch"], capture_output=True, text=True, timeout=20)
        text = (r.stdout or "") + (r.stderr or "")
        for k in SKY:
            if k in text: epoch = k; break
    sky = SKY.get(epoch, "clear")
    h = hashlib.sha256(f"{epoch}:{sky}".encode()).hexdigest()[:8]
    frames = [{"t": "0.0s", "role": "hook", "text": "EPOCH WEATHER", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"{epoch} → {sky}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"sig {h}", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · sky follows ceremony", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "epoch_weather", "epoch": epoch, "sky": sky, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
