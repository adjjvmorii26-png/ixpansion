#!/usr/bin/env python3
"""Dual-track status card — ALEPH vs Lab + caption frames."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def smoke_ok():
    r = subprocess.run([sys.executable, str(REPO / "lab" / "smoke_lab.py")], capture_output=True, text=True, timeout=90)
    try: return bool(json.loads(r.stdout or "{}").get("ok"))
    except json.JSONDecodeError: return r.returncode == 0
def main():
    lab_green = smoke_ok()
    card = {
        "ok": True,
        "ts": datetime.now(timezone.utc).isoformat(),
        "tracks": {
            "lab": {"branch": "lab/chrono-forge-wave", "gates": "Lab Smoke + Lab Graft", "local_smoke": lab_green, "pr": "https://github.com/adjjvmorii26-png/ixpansion/pull/106", "role": "organism overlay · ethics · SEAMWALK · GRAFT"},
            "aleph": {"branch": "main", "gates": "full CI (ci.yml) + wave deploys", "role": "900+ module engine · Dream Forge · Resonance", "note": "deploy can be green while full CI is red"},
        },
        "doctrine": "two greens, one repo — do not confuse the tracks",
        "channel": "@CoodingLooop",
    }
    frames = [
        {"t": "0.0s", "role": "hook", "text": "TWO TRACKS", "style": "void_cyan"},
        {"t": "2.0s", "role": "core", "text": "LAB gates ≠ ALEPH CI", "style": "magenta"},
        {"t": "5.0s", "role": "live", "text": f"lab smoke {'green' if lab_green else 'red'}", "style": "cyan"},
        {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · proof > spectacle", "style": "dim"},
    ]
    card["frames"] = frames
    dest = REPO / "content_output" / "captions"; dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"dual_track_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"
    path.write_text(json.dumps({"ok": True, "frames": frames, "audio": None}, indent=2) + "\n")
    (REPO / "docs" / "DUAL_TRACK.json").write_text(json.dumps(card, indent=2) + "\n")
    card["wrote"] = str(path)
    print(json.dumps(card, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
