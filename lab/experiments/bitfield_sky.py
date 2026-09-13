#!/usr/bin/env python3
"""Bitfield Sky — pack lab health into one constellation int."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
FLAGS = [("chronoforge", REPO / "lab" / "CHRONOFORGE" / "runtime" / "cf_portal.py"), ("carnival", REPO / "lab" / "experiments" / "carnival.py"), ("mercy", REPO / "lab" / "experiments" / "mercy_protocol.py"), ("rail_sync_doc", REPO / "docs" / "LAB_SYNC.md"), ("stratum", REPO / "lab" / "STRATUM_ENGINE")]
BRAILLE = "⠀⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏"
def main():
    bits, lit = 0, []
    for i, (name, path) in enumerate(FLAGS):
        if path.exists():
            bits |= 1 << i; lit.append(name)
    sky = "".join(BRAILLE[(bits >> (i * 2)) & 3] for i in range(4))
    frames = [{"t": "0.0s", "role": "hook", "text": "BITFIELD SKY", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"0b{bits:08b} · {sky}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": ",".join(lit[:4]) or "empty", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · health as constellation", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "bitfield_sky", "bits": bits, "sky": sky, "lit": lit, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
