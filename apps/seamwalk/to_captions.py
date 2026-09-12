#!/usr/bin/env python3
"""SEAMWALK field → @CoodingLooop caption frames."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
def main():
    subprocess.run([sys.executable, str(HERE / "build_seams.py")], check=False, timeout=60)
    data = json.loads((HERE / "seams.json").read_text()) if (HERE / "seams.json").exists() else {}
    field = data.get("field") or []
    rifts = [s for s in field if s.get("kind") == "rift"]
    plates = [s for s in field if s.get("kind") == "plate"]
    frames = [
        {"t": "0.0s", "role": "hook", "text": "SEAMWALK", "style": "void_cyan"},
        {"t": "2.0s", "role": "core", "text": f"{len(plates)} plates · {len(rifts)} rifts", "style": "magenta"},
        {"t": "5.0s", "role": "live", "text": data.get("doctrine") or "absence is structure", "style": "cyan"},
        {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · never fill the void", "style": "dim"},
    ]
    out = {"ok": True, "project": "seamwalk_captions", "mood": data.get("mood"), "n_seams": data.get("n_seams"), "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}
    dest = REPO / "content_output" / "captions"; dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"seamwalk_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(out, indent=2) + "\n"); out["wrote"] = str(path)
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
