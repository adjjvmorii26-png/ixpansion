#!/usr/bin/env python3
"""Diff Garden — bloom of added/removed tokens."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
def toks(s):
    return set(s.replace("\n", " ").split())
def main():
    a, b = "absence is structure silence is the product surface", "absence is structure tide follows proof density"
    if len(sys.argv) >= 3:
        pa, pb = Path(sys.argv[1]), Path(sys.argv[2])
        if pa.exists() and pb.exists():
            a, b = pa.read_text(errors="ignore")[:8000], pb.read_text(errors="ignore")[:8000]
    A, B = toks(a), toks(b)
    added, removed = sorted(B - A)[:12], sorted(A - B)[:12]
    frames = [{"t": "0.0s", "role": "hook", "text": "DIFF GARDEN", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"+{len(added)} / -{len(removed)}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": ("+" + ",".join(added[:3])) if added else "no bloom", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · grow only the delta", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "diff_garden", "added": added, "removed": removed, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
