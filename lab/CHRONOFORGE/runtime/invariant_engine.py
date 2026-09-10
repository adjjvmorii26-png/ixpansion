#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
HEX = HERE.parent / "000_ROOT_SPEC" / "invariants.hex"
def load() -> dict:
    text = HEX.read_text() if HEX.exists() else ""
    items = []
    for m in re.finditer(r"^(INV-\d+)\s+0x([0-9A-Fa-f]+)\s+(\S+)", text, re.M):
        items.append({"id": m.group(1), "addr": m.group(2).upper(), "name": m.group(3)})
    root_m = re.search(r"INVARIANT_SET_ROOT\s+0x([0-9A-Fa-f]+)", text)
    return {"path": str(HEX), "count": len(items), "items": items, "set_root": root_m.group(1).upper() if root_m else None, "ok": len(items) >= 10 and root_m is not None}
if __name__ == "__main__":
    print(json.dumps(load(), indent=2))
