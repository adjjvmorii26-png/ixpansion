#!/usr/bin/env python3
"""Merkle-style root over last N proof ledger lines."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGERS = [ROOT / "lab" / "unique_path" / "proof_ledger.jsonl", ROOT / "unique_path" / "proof_ledger.jsonl"]

def leaf(line: str) -> bytes:
    return hashlib.sha256(line.encode()).digest()

def merkle_root(lines: list[str]) -> str:
    if not lines:
        return hashlib.sha256(b"empty").hexdigest()
    layer = [leaf(x) for x in lines]
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else a
            nxt.append(hashlib.sha256(a + b).digest())
        layer = nxt
    return layer[0].hex()

def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    path = next((p for p in LEDGERS if p.exists()), None)
    if not path:
        print(json.dumps({"ok": False, "error": "no ledger"}))
        return 1
    lines = path.read_text().strip().splitlines()[-n:]
    root = merkle_root(lines)
    out = {"ok": True, "n": len(lines), "root": root, "path": str(path)}
    (Path(__file__).resolve().parent / "proof_merkle_root.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
