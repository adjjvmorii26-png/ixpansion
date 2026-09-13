#!/usr/bin/env python3
"""Echo Archive — index caption JSON by doctrine keywords."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict
REPO = Path(__file__).resolve().parents[2]
CAP = REPO / "content_output" / "captions"
KEYS = ("absence", "silence", "scar", "tide", "graft", "seam", "weather", "choir", "compass", "constellation", "proof")
def main():
    index = defaultdict(list)
    files = sorted(CAP.glob("*.json")) if CAP.exists() else []
    for f in files[-50:]:
        try: text = f.read_text().lower()
        except OSError: continue
        for k in KEYS:
            if k in text: index[k].append(f.name)
    out = {"ok": True, "project": "echo_archive", "files_scanned": min(50, len(files)), "index": {k: v[-5:] for k, v in sorted(index.items())}, "doctrine": "archive the echoes not the noise", "ts": datetime.now(timezone.utc).isoformat()}
    (REPO / "docs").mkdir(exist_ok=True)
    (REPO / "docs" / "ECHO_ARCHIVE.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
