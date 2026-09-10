#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
HEX = Path(__file__).resolve().parent.parent / "PRIME_CORE" / "PRIME_GLYPHS.hex"
def load():
    text = HEX.read_text() if HEX.exists() else ""
    items = [{"id": m.group(1), "addr": m.group(2).upper(), "name": m.group(3)}
             for m in re.finditer(r"^(G\d+)\s+0x([0-9A-Fa-f]+)\s+(\S+)", text, re.M)]
    root = re.search(r"GLYPH_SET_ROOT\s+0x([0-9A-Fa-f]+)", text)
    return {"count": len(items), "items": items, "glyph_set_root": root.group(1).upper() if root else None, "ok": len(items)>=10 and bool(root)}
if __name__=="__main__":
    print(json.dumps(load(), indent=2))
