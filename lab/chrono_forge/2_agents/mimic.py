#!/usr/bin/env python3
"""Mimic — learn last short pattern and emit a variant."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SHORTS = ROOT / "content_output" / "coodinglooop" / "shorts"
PULSE = Path(__file__).resolve().parents[1] / "0_primal_core" / "pulse_state.json"

def mimic() -> dict:
    SHORTS.mkdir(parents=True, exist_ok=True)
    files = sorted(SHORTS.glob("*.md"))
    last = files[-1].read_text() if files else "SIGIL NONE\nPROOF\n"
    lines = [ln for ln in last.strip().splitlines() if ln.strip()][:3]
    pulse = json.loads(PULSE.read_text()) if PULSE.exists() else {}
    sigil = pulse.get("sigil") or "PULSE-XXXX"
    variant = [f"MIMIC {sigil}", lines[1] if len(lines) > 1 else "THE PATTERN HOLDS", "VARIANT · NOT A TEMPLATE"]
    body = "\n".join(variant) + "\n"
    out = SHORTS / f"s_mimic_{sigil.replace('-', '_').lower()}.md"
    out.write_text(body)
    return {"agent": "mimic", "path": str(out), "body": body.strip()}

if __name__ == "__main__":
    print(json.dumps(mimic(), indent=2))
