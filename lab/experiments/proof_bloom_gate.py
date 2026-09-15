#!/usr/bin/env python3
"""Proof Bloom Gate — novelty gate before caption publish."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
def run_bloom():
    p = Path(__file__).resolve().parent / "proof_bloom.py"
    if not p.exists():
        return {"novel": 0, "echo": 0}
    r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True, timeout=25)
    try:
        return json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        return {"novel": 0, "echo": 0}
def main():
    b = run_bloom()
    novel, echo = int(b.get("novel") or 0), int(b.get("echo") or 0)
    total = max(1, novel + echo)
    ratio = novel / total
    publish_ok = ratio >= 0.35 or novel >= 3
    decision = "PUBLISH" if publish_ok else "HOLD_ARCHIVE"
    frames = [{"t": "0.0s", "role": "hook", "text": "PROOF BLOOM GATE", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": decision, "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"novel {novel}/{total} ({ratio:.0%})", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · only the new surface", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "proof_bloom_gate", "publish_ok": publish_ok, "decision": decision, "novel": novel, "echo": echo, "ratio": round(ratio, 3), "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
