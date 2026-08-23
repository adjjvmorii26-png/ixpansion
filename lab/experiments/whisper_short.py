#!/usr/bin/env python3
"""3-line caption short from pulse sigil alone."""
from __future__ import annotations
import json
from pathlib import Path

PULSE = Path(__file__).resolve().parents[1] / "chrono_forge" / "0_primal_core" / "pulse_state.json"
OUT = Path(__file__).resolve().parents[2] / "content_output" / "coodinglooop" / "shorts"

def main() -> None:
    st = json.loads(PULSE.read_text()) if PULSE.exists() else {"sigil": "PULSE-0000", "beats": 0}
    sigil = st.get("sigil") or "PULSE-0000"
    body = f"SIGIL {sigil}\nTHE PULSE DOES NOT ADVERTISE\nIT LEAVES PROOF\n"
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"s_whisper_{sigil.replace('-','_').lower()}.md"
    path.write_text(body)
    print(json.dumps({"path": str(path), "body": body.strip()}))

if __name__ == "__main__":
    main()
