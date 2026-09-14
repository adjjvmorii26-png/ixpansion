#!/usr/bin/env python3
"""Hex Bundle — consent + mercy hexsrc package for hexrun."""
from __future__ import annotations
import json, hashlib, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
def ensure(script, *args):
    p = EXP / script
    if p.exists():
        subprocess.run([sys.executable, str(p), *args], capture_output=True, text=True, timeout=20)
def main():
    ensure("hex_from_consent.py")
    ensure("hex_from_mercy.py", "delete ci workflow")
    parts = []
    for name in ("consent_program.hexsrc", "mercy_program.hexsrc"):
        f = EXP / name
        if f.exists():
            parts.append(f"; ---- {name} ----\n" + f.read_text())
    body = "\n".join(parts) if parts else "; empty bundle\nHALT\n"
    h = hashlib.sha256(body.encode()).hexdigest()[:16]
    out = EXP / "organism_bundle.hexsrc"
    out.write_text(f"; bundle {h}\n" + body)
    frames = [{"t": "0.0s", "role": "hook", "text": "HEX BUNDLE", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": h, "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"{len(parts)} segments", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · one package for hexrun", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "hex_bundle", "hash": h, "segments": len(parts), "path": str(out.relative_to(REPO)), "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
