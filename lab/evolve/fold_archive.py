#!/usr/bin/env python3
"""Fold Archive — propose folds when pressure is watch/fold_now."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def main():
    pressure, band = 0.0, "hold"
    fp = REPO / "lab" / "evolve" / "fold_pressure.py"
    if fp.exists():
        r = subprocess.run([sys.executable, str(fp)], capture_output=True, text=True, timeout=30)
        try:
            j = json.loads(r.stdout or "{}")
            pressure, band = j.get("pressure", 0), j.get("band", "hold")
        except json.JSONDecodeError: pass
    proposals = []
    if band in ("watch", "fold_now"):
        proposals = [
            {"fold": "caption_tools", "into": "caption_lattice", "why": "many caption emitters"},
            {"fold": "dream_* experiments", "into": "dream_residue", "why": "shared almost-organ metaphor"},
            {"fold": "stale lab branch docs", "into": "docs/LAB_SYNC.md", "why": "one sync policy"},
        ]
    frames = [{"t": "0.0s", "role": "hook", "text": "FOLD ARCHIVE", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"{band} · {pressure}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"{len(proposals)} proposals", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · densify on purpose", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "fold_archive", "band": band, "pressure": pressure, "proposals": proposals, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
