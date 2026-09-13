#!/usr/bin/env python3
"""Meaning Density — doctrine roots / module count."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def count_py(folder):
    p = REPO / folder
    return len(list(p.rglob("*.py"))) if p.exists() else 0
def main():
    ops, exp, proj, evo = count_py("lab/ops"), count_py("lab/experiments"), count_py("lab/projects"), count_py("lab/evolve")
    total = ops + exp + proj + evo
    n_doc = 0
    man = REPO / "lab" / "LAB_MANIFEST.json"
    if man.exists():
        try: n_doc = len(json.loads(man.read_text()).get("doctrine") or [])
        except json.JSONDecodeError: pass
    density = round(n_doc / max(1, total), 4)
    frames = [{"t": "0.0s", "role": "hook", "text": "MEANING DENSITY", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"{n_doc} doctrine / {total} modules", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"density {density}", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · fewer organs denser meaning", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "meaning_density", "modules": {"ops": ops, "experiments": exp, "projects": proj, "evolve": evo, "total": total}, "doctrine_n": n_doc, "density": density, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
