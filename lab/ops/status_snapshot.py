#!/usr/bin/env python3
"""Write a compact local status snapshot for the dashboard / heartbeat."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT_JSON = ROOT / "docs" / "LAB_STATUS.json"
OUT_MD = ROOT / "docs" / "LAB_STATUS.md"


def main() -> int:
    try:
        from lab.ops.copilots.council import run_council

        package = run_council()
    except Exception as e:
        package = {"ok": False, "error": str(e)}

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat()
    snap = {
        "updated": stamp,
        "source": "lab.ops.status_snapshot",
        "council": package,
    }
    OUT_JSON.write_text(json.dumps(snap, indent=2) + "\n")

    scan = ((package.get("aegis") or {}).get("scan") or {}) if isinstance(package, dict) else {}
    helix = (package.get("helix") or {}) if isinstance(package, dict) else {}
    next_w = helix.get("next") or {}
    quill = (package.get("quill") or {}) if isinstance(package, dict) else {}
    md = "\n".join(
        [
            f"# Lab Status · {stamp}",
            "",
            f"- **AEGIS:** `{scan.get('posture', 'n/a')}`",
            f"- **HELIX next:** `{next_w.get('module', 'n/a')}`",
            f"- **QUILL:** {quill.get('headline', 'n/a')}",
            "",
            "```bash",
            "make council",
            "make dashboard",
            "make shell",
            "```",
            "",
            "Caption: `aegis · helix · quill · local`",
            "",
        ]
    )
    OUT_MD.write_text(md)
    print(f"wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
