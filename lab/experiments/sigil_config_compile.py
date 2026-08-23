#!/usr/bin/env python3
"""Compile HEX sigils into MFE remote config fragments."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "sigil_mfe_configs.json"

def sigil(name: str) -> str:
    return "0x" + hashlib.sha256(name.encode()).hexdigest()[:8].upper()

def compile_remotes(names: list[str]) -> dict:
    remotes = []
    for n in names:
        s = sigil(n)
        remotes.append({
            "name": n, "sigil": s,
            "route": f"/{n.replace('_', '-')}",
            "entry": f"/mfe/remotes/{n}.html",
            "title": n.replace("_", " ").title(),
            "color_hint": f"#{s[2:8]}",
        })
    out = {"version": 1, "remotes": remotes}
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    return out

if __name__ == "__main__":
    print(json.dumps(compile_remotes([
        "sandbox_live", "proof_desk", "glyph_ui", "chronicle", "wanderer_board"
    ]), indent=2))
