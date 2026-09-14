#!/usr/bin/env python3
"""Hex Cathedral builder — emits a laced organism bundle."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "lab" / "experiments" / "organism_cathedral.hexsrc"
CONSENT = OUT.parent / "consent_program.hexsrc"
MERCY = OUT.parent / "mercy_program.hexsrc"
def _have_chapel(p: Path) -> bool:
    return p.exists() and "; #chapel" in p.read_text()
def main():
    if not CONSENT.exists() or not MERCY.exists():
        return {"ok": False, "error": "missing consent/mercy hexsrc"}
    consent = CONSENT.read_text()
    mercy = MERCY.read_text()
    if not _have_chapel(CONSENT):
        consent = "; #chapel consent_chapel\n" + consent
    if not _have_chapel(MERCY):
        mercy = "; #chapel mercy_chapel\n" + mercy
    body = f"; ---- consent_program.hexsrc ----\n{consent}\n; ---- mercy_program.hexsrc ----\n{mercy}"
    h = hashlib.sha256(body.encode()).hexdigest()[:16]
    OUT.write_text(f"; cathedral {h}\n" + body)
    print(json.dumps({"ok": True, "project": "hex_cathedral", "path": str(OUT.relative_to(REPO)), "hash": h, "chapels": 2, "ts": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}, indent=2))
    return 0
if __name__ == "__main__":
    raise SystemExit(main() or 0)
