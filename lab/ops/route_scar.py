#!/usr/bin/env python3
"""Route Scar — vercel route collapse as scar tissue / caption memory."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
SCAR = {"event": "vercel_route_collapse", "before": 754, "after": 89, "wave": 409, "note": "over-escaped regexes removed · catch-all /api/:path*"}
def heal_ratio(before, after):
    return round(1.0 - (after / before), 4) if before > 0 else 0.0
def main():
    r = heal_ratio(SCAR["before"], SCAR["after"])
    frames = [
        {"t": "0.0s", "role": "hook", "text": "ROUTE SCAR", "style": "void_cyan"},
        {"t": "2.0s", "role": "core", "text": f"{SCAR['before']} → {SCAR['after']} routes", "style": "magenta"},
        {"t": "5.0s", "role": "live", "text": f"healed {r*100:.1f}% surface · wave {SCAR['wave']}", "style": "cyan"},
        {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · less map, more organism", "style": "dim"},
    ]
    out = {"ok": True, "project": "route_scar", "scar": SCAR, "heal_ratio": r, "frames": frames, "audio": None, "doctrine": "compression is memory, not deletion", "ts": datetime.now(timezone.utc).isoformat()}
    dest = Path(__file__).resolve().parents[2] / "content_output" / "captions"
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"route_scar_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"
    path.write_text(json.dumps({"ok": True, "frames": frames, "audio": None}, indent=2) + "\n")
    out["wrote"] = str(path)
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
