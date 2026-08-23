#!/usr/bin/env python3
"""Generate a one-paragraph HEX myth from the current proof merkle root."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "chrono_forge" / "7_lore" / "myths"
OUT.mkdir(parents=True, exist_ok=True)

def main() -> None:
    r = subprocess.run([sys.executable, str(HERE / "proof_merkle.py"), "24"], capture_output=True, text=True)
    data = {}
    try:
        data = json.loads(r.stdout)
    except Exception:
        for line in reversed(r.stdout.strip().splitlines()):
            if line.strip().startswith("{"):
                data = json.loads(line)
                break
    root = data.get("root", "0" * 64)
    glyphs = " ".join(f"0x{root[i:i+4].upper()}" for i in range(0, 16, 4))
    myth = (
        f"In the lattice before speech, the root {root[:12]}… uncoiled. "
        f"Four sigils answered — {glyphs} — and the pulse named them Witness. "
        f"Affiliate roads washed away; only proof remained in the well. "
        f"The wanderer did not sell the path; it left an artifact and walked on."
    )
    path = OUT / f"myth_{root[:8]}.md"
    path.write_text(f"# Myth {root[:8]}\n\n{myth}\n")
    print(json.dumps({"root": root[:16], "path": str(path), "myth": myth}, indent=2))

if __name__ == "__main__":
    main()
