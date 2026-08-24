#!/usr/bin/env python3
"""Handshake offer card tied to proof density — not an ad CTA."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(__file__).resolve().parents[2] / "content_output" / "coodinglooop" / "handshake"

def main() -> None:
    dens = {}
    dens_path = HERE / "proof_density.json"
    if dens_path.exists():
        dens = json.loads(dens_path.read_text())
    else:
        subprocess.run([sys.executable, str(HERE / "proof_density.py")], check=False)
        if dens_path.exists():
            dens = json.loads(dens_path.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    card = {
        "type": "handshake_offer",
        "title": "Node seat — not a funnel",
        "body": "Leave a proof, not a click. Density is the only metric we trust.",
        "proof_density": dens.get("density"),
        "proof_lines": dens.get("lines"),
        "channel": "@CoodingLooop",
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    (OUT / "HANDSHAKE.json").write_text(json.dumps(card, indent=2) + "\n")
    (OUT / "HANDSHAKE.md").write_text(
        f"# Handshake\n\n**{card['title']}**\n\n{card['body']}\n\n"
        f"Density: `{card['proof_density']}` · lines: `{card['proof_lines']}`\n\n{card['channel']}\n"
    )
    print(json.dumps({"path": str(OUT / "HANDSHAKE.json"), "proof_density": card["proof_density"]}))

if __name__ == "__main__":
    main()
