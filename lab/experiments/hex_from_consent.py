#!/usr/bin/env python3
"""Hex-from-Consent — Wave-97-style mnemonic from consent lattice."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def load_scopes():
    reg = REPO / "lab" / "experiments" / "consent_registry.json"
    if reg.exists():
        try: return json.loads(reg.read_text()).get("scopes") or {}
        except json.JSONDecodeError: pass
    return {"read_lab": True, "delete_ci": False, "push_main": False}
def to_hex_src(scopes: dict) -> str:
    lines = ["; auto from consent_lattice", "; #chapel consent_chapel"]
    lines += ["PUSH 1"]
    for k, v in sorted(scopes.items()):
        lines += [f"; scope {k}", f"PUSH {1 if v else 0}", "ADD"]
    lines += ["; #altar consent_hall", "GLYPH", "ENACT", "HALT"]
    return "\n".join(lines)
def main():
    scopes = load_scopes()
    src = to_hex_src(scopes)
    out = REPO / "lab" / "experiments" / "consent_program.hexsrc"
    out.write_text(src + "\n")
    frames = [{"t": "0.0s", "role": "hook", "text": "HEX FROM CONSENT", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"{len(scopes)} scopes → mnemonic", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": "GLYPH · ENACT · HALT", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · ethics compiles", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "hex_from_consent", "scopes": scopes, "path": str(out.relative_to(REPO)), "src_preview": src[:400], "frames": frames, "audio": None, "note": "feed to hexrun on main", "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
