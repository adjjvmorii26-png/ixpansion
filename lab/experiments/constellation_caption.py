#!/usr/bin/env python3
"""5-line caption board from constellation node sigils."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONST = HERE / "constellation.json"
OUT = Path(__file__).resolve().parents[2] / "content_output" / "coodinglooop" / "shorts"

def main() -> None:
    if not CONST.exists():
        subprocess.check_call([sys.executable, str(HERE / "sigil_constellation.py")])
    g = json.loads(CONST.read_text())
    nodes = g.get("nodes") or []
    lines = ["CONSTELLATION · NOT AN AD"]
    for n in nodes[:4]:
        lines.append(f"{n['id'].upper()} {n['sigil']}")
    lines.append("PROOF LEDGER · @CoodingLooop")
    body = "\n".join(lines) + "\n"
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "s_constellation.md"
    path.write_text(body)
    print(json.dumps({"path": str(path), "lines": len(lines)}))

if __name__ == "__main__":
    main()
