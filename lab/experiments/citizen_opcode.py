#!/usr/bin/env python3
"""Citizen Opcode — roles mapped to allowed hex ops (lab bridge to Wave 666)."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
ROLES = {
    "observer": {"ops": ["PUSH", "HALT", "GLYPH"], "enact": False},
    "worker": {"ops": ["PUSH", "ADD", "XOR", "DUP", "HALT", "GLYPH"], "enact": False},
    "steward": {"ops": ["PUSH", "ADD", "XOR", "DUP", "JMPZ", "GLYPH", "ENACT", "HALT"], "enact": True},
    "citizen": {"ops": ["PUSH", "ADD", "GLYPH", "HALT"], "enact": False},
}
def compile_for(role: str, intent: str = "status") -> str:
    r = ROLES.get(role, ROLES["observer"])
    lines = [f"; citizen role={role} intent={intent[:40]}"]
    if r["enact"] and intent.startswith("enact"):
        lines += ["PUSH 1", "ENACT", "GLYPH", "HALT"]
    elif "GLYPH" in r["ops"]:
        lines += ["PUSH 1", "GLYPH", "HALT"]
    else:
        lines += ["PUSH 0", "HALT"]
    return "\n".join(lines)
def main():
    role = (sys.argv[1] if len(sys.argv) > 1 else "steward").lower()
    intent = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "enact census"
    if role not in ROLES:
        role = "observer"
    src = compile_for(role, intent)
    out = Path(__file__).resolve().parent / f"citizen_{role}.hexsrc"
    out.write_text(src + "\n")
    frames = [{"t": "0.0s", "role": "hook", "text": "CITIZEN OPCODE", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"{role} · enact={ROLES[role]['enact']}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": ",".join(ROLES[role]["ops"][:4]), "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · rights before runtime", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "citizen_opcode", "role": role, "allowed_ops": ROLES[role]["ops"], "enact": ROLES[role]["enact"], "path": str(out.relative_to(REPO)), "src_preview": src, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
