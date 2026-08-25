#!/usr/bin/env python3
"""Braid last N proof types into a compact glyph string for captions."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "lab" / "unique_path" / "proof_ledger.jsonl"
OUT = Path(__file__).resolve().parent / "glyph_braid.txt"
MAP = {
    "ship": "◈", "artifact": "◆", "sandbox_ticks": "◎",
    "pinned_run": "◉", "creative_wave": "✧", "doctrine": "◇",
    "bootstrap": "○", "caretaker_pass": "▣",
}

def braid(n: int = 12) -> str:
    if not LEDGER.exists():
        return "·"
    types = []
    for ln in LEDGER.read_text().strip().splitlines()[-n:]:
        try:
            types.append(json.loads(ln).get("type", "?"))
        except Exception:
            types.append("?")
    glyphs = "".join(MAP.get(t, "·") for t in types)
    OUT.write_text(glyphs + "\n")
    print(json.dumps({"braid": glyphs, "n": len(types)}))
    return glyphs

if __name__ == "__main__":
    braid()
