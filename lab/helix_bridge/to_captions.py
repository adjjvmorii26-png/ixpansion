#!/usr/bin/env python3
"""Turn HB-1 constellation into caption frames."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
def main() -> int:
    subprocess.run([sys.executable, str(HERE / "probe.py")], check=False, timeout=90)
    data = json.loads((HERE / "constellation.json").read_text()) if (HERE / "constellation.json").exists() else {}
    nodes = data.get("nodes") or []
    ok_n = sum(1 for n in nodes if n.get("ok"))
    frames = [
        {"t": "0.0s", "role": "hook", "text": "HELIX BRIDGE · organism constellation", "style": "void_cyan"},
        {"t": "2.5s", "role": "core", "text": f"{ok_n}/{len(nodes)} portals ethics-green", "style": "magenta"},
        {"t": "5.0s", "role": "live", "text": " · ".join(n["name"] for n in nodes if n.get("ok"))[:80] or "none", "style": "cyan"},
        {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · proof > spectacle", "style": "dim"},
    ]
    out = {"ok": bool(data.get("ok")), "project": "helix_captions", "protocol": data.get("protocol"), "frames": frames, "ts": datetime.now(timezone.utc).isoformat(), "audio": None}
    dest = REPO / "content_output" / "captions"
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"helix_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    out["wrote"] = str(path)
    print(json.dumps(out, indent=2))
    return 0 if out["ok"] else 1
if __name__ == "__main__":
    raise SystemExit(main())
