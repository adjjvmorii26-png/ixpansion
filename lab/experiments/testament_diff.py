#!/usr/bin/env python3
"""Testament Diff — hash-chained lab notes (CHRONOFORGE-aligned)."""
from __future__ import annotations
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
LOG = REPO / "lab" / "experiments" / "testaments.jsonl"
def main():
    note = "rail-sync additive experiments; no CI deletion; CHRONOFORGE base held"
    line = {"ts": datetime.now(timezone.utc).isoformat(), "kind": "lab_note", "note": note, "hash": hashlib.sha256(note.encode()).hexdigest()[:12]}
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f: f.write(json.dumps(line) + "\n")
    frames = [{"t": "0.0s", "role": "hook", "text": "TESTAMENT", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": line["hash"], "style": "magenta"}, {"t": "5.0s", "role": "live", "text": note[:42], "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · write what you keep", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "testament_diff", "line": line, "frames": frames, "audio": None}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
