#!/usr/bin/env python3
"""Proof Tide — hash spine of proof artifacts."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def spine():
    paths, out, prev = [], [], b""
    for folder in [REPO/"content_output"/"captions", REPO/"lab"/"ops"/"graft_reports", REPO/"docs"]:
        if folder.exists():
            paths.extend(sorted(folder.glob("*.json"))[-12:])
    for f in paths:
        h = hashlib.sha256(prev + f.read_bytes()[:2048]).hexdigest()[:12]
        out.append(h); prev = h.encode()
    return out
def main():
    s = spine(); n = len(s); level = min(1.0, n/20.0); phase = "rising" if level >= 0.35 else "ebb"
    frames = [{"t":"0.0s","role":"hook","text":"PROOF TIDE","style":"void_cyan"},{"t":"2.0s","role":"core","text":f"{phase} · level {level:.2f}","style":"magenta"},{"t":"5.0s","role":"live","text":f"spine×{n}","style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · ride the ledger","style":"dim"}]
    out = {"ok": True, "project": "proof_tide", "phase": phase, "level": level, "spine": s[-8:], "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}
    dest = REPO/"content_output"/"captions"; dest.mkdir(parents=True, exist_ok=True)
    (dest / f"proof_tide_{datetime.now(timezone.utc).strftime('%H%M%S')}.json").write_text(json.dumps({"ok": True, "frames": frames, "audio": None}, indent=2)+"\n")
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
