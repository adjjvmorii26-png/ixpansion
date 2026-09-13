#!/usr/bin/env python3
"""Silence Ledger — caption deposits as silence capital."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
CAP = REPO / "content_output" / "captions"
def main():
    files = sorted(CAP.glob("*.json")) if CAP.exists() else []
    deposits, total = [], 0
    for f in files[-40:]:
        try: data = json.loads(f.read_text())
        except json.JSONDecodeError: continue
        frames = data.get("frames") or []; total += len(frames)
        deposits.append({"file": f.name, "frames": len(frames), "audio": data.get("audio")})
    print(json.dumps({"ok": True, "project": "silence_ledger", "deposits": len(deposits), "frame_capital": total, "audio_files": 0, "doctrine": "silence is the product surface", "recent": deposits[-8:], "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
