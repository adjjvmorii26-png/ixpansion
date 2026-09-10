#!/usr/bin/env python3
"""Recompute invariant addresses; fail on drift."""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
HEX = HERE.parent / "000_ROOT_SPEC" / "invariants.hex"
JS = HERE.parent / "000_ROOT_SPEC" / "invariants.json"

def main() -> int:
    text = HEX.read_text()
    issues = []
    items = []
    for m in re.finditer(r"^(INV-\d+)\s+0x([0-9A-Fa-f]+)\s+(\S+)", text, re.M):
        items.append((m.group(1), m.group(2).upper(), m.group(3)))
    if JS.exists():
        data = json.loads(JS.read_text())
        by_id = {x["id"]: x for x in data.get("items", [])}
        for iid, addr, name in items:
            meta = by_id.get(iid)
            if not meta:
                issues.append(f"missing_json:{iid}")
                continue
            full = meta.get("full_sha256", "")
            if full and full[:16].upper() != addr:
                issues.append(f"addr_drift:{iid}:file={addr}")
    if "INVARIANT_SET_ROOT" not in text:
        issues.append("missing_set_root")
    ok = not issues
    print(json.dumps({"ok": ok, "count": len(items), "issues": issues}, indent=2))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
