#!/usr/bin/env python3
"""Palimpsest — stack first-lines of lab READMEs."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def main():
    layers = []
    for p in sorted((REPO / "lab").rglob("README.md"))[:24]:
        try:
            line = next((ln.strip() for ln in p.read_text(errors="ignore").splitlines() if ln.strip()), "")
        except OSError:
            continue
        if line:
            layers.append({"path": str(p.relative_to(REPO)), "line": line[:80]})
    frames = [{"t": "0.0s", "role": "hook", "text": "PALIMPSEST", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"{len(layers)} layers", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": (layers[0]["line"][:40] if layers else "empty"), "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · read through the pages", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "palimpsest", "n": len(layers), "layers": layers[:12], "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
