#!/usr/bin/env python3
"""Silence Ledger — caption-only deposits as silence capital."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
CAP = REPO / "content_output" / "captions"
def main():
    files = sorted(CAP.glob("*.json")) if CAP.exists() else []
    deposits, total_frames = [], 0
    for f in files[-40:]:
        try: data = json.loads(f.read_text())
        except json.JSONDecodeError: continue
        frames = data.get("frames") or []
        total_frames += len(frames)
        deposits.append({"file": f.name, "frames": len(frames), "audio": data.get("audio")})
    out = {"ok": True, "project": "silence_ledger", "deposits": len(deposits), "frame_capital": total_frames, "audio_files": 0, "doctrine": "silence is the product surface", "channel": "@CoodingLooop", "recent": deposits[-8:], "ts": datetime.now(timezone.utc).isoformat()}
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
