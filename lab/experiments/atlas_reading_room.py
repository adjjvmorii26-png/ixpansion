#!/usr/bin/env python3
"""Atlas Reading Room — quiet doctrine shelves."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
DOCS = [REPO / "docs" / "IXPANSION_2036.md", REPO / "docs" / "WAVE_ROADMAP_432_450.md", REPO / "docs" / "AGENTS_EXPANDED.md"]
def main():
    shelves = []
    for p in DOCS:
        if p.exists():
            lines = [ln.strip() for ln in p.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
            shelves.append({"shelf": p.name, "lines": lines[:6]})
    room = {"ok": True, "project": "atlas_reading_room", "shelves": shelves, "doctrine": "read rooms beat control panels", "frames": [{"t": "0.0s", "role": "hook", "text": "READING ROOM", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"{len(shelves)} shelves open", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": "quiet atlas · no feed", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · sit with the text", "style": "dim"}], "audio": None, "ts": datetime.now(timezone.utc).isoformat()}
    out = REPO / "docs" / "READING_ROOM.json"; out.write_text(json.dumps(room, indent=2) + "\n"); room["wrote"] = str(out)
    print(json.dumps(room, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
