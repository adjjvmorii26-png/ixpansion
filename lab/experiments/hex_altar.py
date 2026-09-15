#!/usr/bin/env python3
"""Hex Altar — merge citizen/mercy/consent hexsrc for hexrun."""
from __future__ import annotations
import json, hashlib, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
EXP = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[2]
def ensure(script, *args):
    p = EXP / script
    if p.exists():
        subprocess.run([sys.executable, str(p), *args], capture_output=True, text=True, timeout=25)
def main():
    ensure("citizen_opcode.py", "steward", "enact altar")
    ensure("hex_from_mercy.py", "delete ci workflow")
    ensure("hex_from_consent.py")
    parts = []
    for name in sorted(EXP.glob("*.hexsrc")):
        if name.name.startswith("organism"):
            continue
        parts.append(f"; #altar {name.name}\n" + name.read_text())
    body = "\n".join(parts) if parts else "; empty\nHALT\n"
    h = hashlib.sha256(body.encode()).hexdigest()[:16]
    out = EXP / "altar_bundle.hexsrc"
    out.write_text(f"; altar {h}\n" + body)
    frames = [{"t": "0.0s", "role": "hook", "text": "HEX ALTAR", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": h, "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"{len(parts)} offerings", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · one altar for hexrun", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "hex_altar", "hash": h, "offerings": len(parts), "path": str(out.relative_to(REPO)), "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
