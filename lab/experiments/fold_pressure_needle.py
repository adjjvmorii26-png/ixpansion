#!/usr/bin/env python3
"""Fold Pressure Needle — experiments/tests ratio as pressure zone."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def main():
    exp = list((REPO / "lab" / "experiments").glob("*.py")) if (REPO / "lab" / "experiments").exists() else []
    tst = list((REPO / "tests").glob("test_lab*.py")) if (REPO / "tests").exists() else []
    n_e, n_t = len(exp), max(1, len(tst))
    pressure = round(n_e / n_t, 2)
    zone = "calm" if pressure < 8 else ("stir" if pressure < 20 else "fold")
    frames = [{"t": "0.0s", "role": "hook", "text": "FOLD PRESSURE", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"{pressure}× · {zone}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"{n_e} exp / {n_t} lab-tests", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · pressure is signal", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "fold_pressure_needle", "experiments": n_e, "lab_tests": n_t, "pressure": pressure, "zone": zone, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
