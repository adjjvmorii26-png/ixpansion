#!/usr/bin/env python3
"""Fold Pressure — sprawl vs doctrine density."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def main():
    dens = {}
    p = REPO / "lab" / "evolve" / "meaning_density.py"
    if p.exists():
        r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True, timeout=30)
        try: dens = json.loads(r.stdout or "{}")
        except json.JSONDecodeError: pass
    total = (dens.get("modules") or {}).get("total") or 1
    n_doc = dens.get("doctrine_n") or 1
    density = dens.get("density") or (n_doc / total)
    pressure = round(max(0.0, min(1.0, 1.0 - float(density) * 5)), 3)
    band = "fold_now" if pressure > 0.7 else ("watch" if pressure > 0.4 else "hold")
    frames = [{"t": "0.0s", "role": "hook", "text": "FOLD PRESSURE", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"{band} · {pressure}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"{total} modules · {n_doc} doctrine", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · fold before sprawl", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "fold_pressure", "pressure": pressure, "band": band, "density": density, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
