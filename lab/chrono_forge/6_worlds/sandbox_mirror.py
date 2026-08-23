#!/usr/bin/env python3
"""Mirror world — invert novelty sign into parallel state file."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "sandbox" / "sandbox_state.json"
DST = Path(__file__).resolve().parent / "mirror_state.json"

def mirror() -> dict:
    st = json.loads(SRC.read_text()) if SRC.exists() else {}
    nov = float(st.get("novelty") or 0)
    out = {
        "world": "sandbox_mirror",
        "ticks": st.get("ticks"),
        "novelty_inverted": round(-nov, 4),
        "entropy_budget": st.get("entropy_budget"),
        "phase_reflected": round((3.14159265 - float(st.get("phase") or 0)) % 6.2832, 4),
        "note": "inverted novelty; not a second physics engine",
    }
    DST.write_text(json.dumps(out, indent=2) + "\n")
    return out

if __name__ == "__main__":
    print(json.dumps(mirror(), indent=2))
