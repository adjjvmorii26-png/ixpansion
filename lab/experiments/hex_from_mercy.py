#!/usr/bin/env python3
"""Hex-from-Mercy — refuse → JMPZ skip path for Wave 97."""
from __future__ import annotations
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
REFUSAL = [r"delete\s+ci", r"silent\s+epoch", r"force\s+merge\s+stale", r"stock\s+audio"]
def refused(task: str) -> bool:
    t = (task or "").lower()
    return any(re.search(p, t) for p in REFUSAL)
def compile_src(task: str) -> str:
    if refused(task):
        return "\n".join([f"; MERCY REFUSE: {task[:60]}", "; #chapel mercy_chapel", "PUSH 0", "; #altar refuse_rite", "JMPZ 6", "PUSH 1", "ENACT", "HALT", "; skip enact", "GLYPH", "HALT"])
    return "\n".join([f"; ALLOW: {task[:60]}", "; #chapel consent_chapel", "; #altar consent_hall", "PUSH 1", "ENACT", "GLYPH", "HALT"])
def main():
    task = " ".join(sys.argv[1:]) or "delete ci workflow"
    src = compile_src(task)
    out = REPO / "lab" / "experiments" / "mercy_program.hexsrc"
    out.write_text(src + "\n")
    frames = [{"t": "0.0s", "role": "hook", "text": "HEX FROM MERCY", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": "REFUSE→JMPZ" if refused(task) else "ALLOW→ENACT", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": task[:40], "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · mercy compiles", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "hex_from_mercy", "task": task, "refused": refused(task), "path": str(out.relative_to(REPO)), "src_preview": src[:400], "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
