#!/usr/bin/env python3
"""HEX sigils for modules — aesthetic IDs, stable from name."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

REG = Path(__file__).resolve().parent / "sigils.json"

def sigil(name: str) -> str:
    h = hashlib.sha256(name.encode()).hexdigest()[:8].upper()
    return f"0x{h}"

def register(name: str) -> dict:
    data = {"sigils": {}}
    try:
        if REG.exists():
            data = json.loads(REG.read_text())
    except Exception:
        pass
    s = sigil(name)
    data.setdefault("sigils", {})[name] = s
    try:
        REG.write_text(json.dumps(data, indent=2) + "\n")
    except OSError:
        pass
    return {"name": name, "sigil": s}

if __name__ == "__main__":
    names = sys.argv[1:] or ["forge_mind", "wanderer", "archivist", "sentinel", "mimic", "pulse_driver"]
    for n in names:
        print(json.dumps(register(n)))
