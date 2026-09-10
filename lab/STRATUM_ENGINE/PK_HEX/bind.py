#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
REPO = Path(__file__).resolve().parents[3]
INV = REPO / "lab" / "CHRONOFORGE" / "000_ROOT_SPEC" / "invariants.hex"
GLY = REPO / "lab" / "MONOLITH_STACK" / "PRIME_CORE" / "PRIME_GLYPHS.hex"
def _root(path, key):
    if not path.exists(): return None
    m = re.search(rf"{key}\s+0x([0-9A-Fa-f]+)", path.read_text())
    return m.group(1).upper() if m else None
def bind(decision):
    return {"ok": True, "decision": decision, "pk": {"invariant_set_root": _root(INV, "INVARIANT_SET_ROOT"), "glyph_set_root": _root(GLY, "GLYPH_SET_ROOT"), "bound": True}}
if __name__ == "__main__":
    print(json.dumps(bind({"action": "observe", "protocol": "ELRP-1"}), indent=2))
