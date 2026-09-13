#!/usr/bin/env python3
"""Mirror Well — density + doctrine into one caption well."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def jrun(rel):
    p = REPO / rel
    if not p.exists(): return {}
    r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True, timeout=40)
    try: return json.loads(r.stdout or "{}")
    except json.JSONDecodeError: return {}
def main():
    dens, dd = jrun("lab/evolve/meaning_density.py"), jrun("lab/projects/doctrine_diff.py")
    frames = [{"t": "0.0s", "role": "hook", "text": "MIRROR WELL", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"density {dens.get('density', '?')}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"doctrine {dd.get('coverage', '?')}", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · the well only reflects", "style": "dim"}]
    out = {"ok": True, "project": "mirror_well", "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}
    dest = REPO / "content_output" / "captions"; dest.mkdir(parents=True, exist_ok=True)
    (dest / f"mirror_{datetime.now(timezone.utc).strftime('%H%M%S')}.json").write_text(json.dumps({"ok": True, "frames": frames, "audio": None}, indent=2) + "\n")
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
