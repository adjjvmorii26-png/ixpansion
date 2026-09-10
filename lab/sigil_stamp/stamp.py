#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, sys
BLOCKS = " ░▒▓█"
def stamp(name):
    h = hashlib.sha256(name.encode()).hexdigest()
    rows = []
    for r in range(5):
        row = "".join(BLOCKS[int(h[(r*11+c)%len(h)], 16)%5] for c in range(11))
        rows.append(row)
    return {"ok": True, "project": "sigil_stamp", "name": name, "sigil": "0x"+h[:12].upper(), "seal": rows, "seal_text": "\n".join(rows)}
if __name__ == "__main__":
    print(json.dumps(stamp(sys.argv[1] if len(sys.argv)>1 else "ixpansion"), indent=2))
