#!/usr/bin/env python3
"""Proof Tide — daily rise/fall of proof artifacts as tide + captions."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def spine():
    paths = []
    for folder in [REPO / "content_output" / "captions", REPO / "lab" / "ops" / "graft_reports", REPO / "docs"]:
        if not folder.exists(): continue
        for f in sorted(folder.glob("*.json"))[-12:]:
            paths.append(f)
    out, prev = [], b""
    for f in paths:
        h = hashlib.sha256(prev + f.read_bytes()[:2048]).hexdigest()[:12]
        out.append(h); prev = h.encode()
    return out
def main():
    s = spine(); n = len(s); level = min(1.0, n / 20.0)
    phase = "rising" if level >= 0.35 else "ebb"
    frames = [
        {"t": "0.0s", "role": "hook", "text": "PROOF TIDE", "style": "void_cyan"},
        {"t": "2.0s", "role": "core", "text": f"{phase} · level {level:.2f}", "style": "magenta"},
        {"t": "5.0s", "role": "live", "text": f"spine×{n} · {s[-1] if s else 'empty'}", "style": "cyan"},
        {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · ride the ledger not the hype", "style": "dim"},
    ]
    out = {"ok": True, "project": "proof_tide", "phase": phase, "level": level, "spine": s[-8:], "frames": frames, "audio": None, "doctrine": "tide follows proof density", "ts": datetime.now(timezone.utc).isoformat()}
    dest = REPO / "content_output" / "captions"; dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"proof_tide_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"
    path.write_text(json.dumps({"ok": True, "frames": frames, "audio": None}, indent=2) + "\n")
    out["wrote"] = str(path)
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
