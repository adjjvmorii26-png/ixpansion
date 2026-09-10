#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
PROOF = REPO / "lab" / "unique_path" / "proof_ledger.jsonl"
MYTH = REPO / "lab" / "mirror_ledger" / "mythos.jsonl"
TEMPLATES = ["In the lattice, {event} became a sealed chord.", "The vault remembered: {event}.", "Under cyan void, {event} refused spectacle.", "Glyphs aligned when {event}."]
def mythos_line(event):
    i = int(hashlib.sha256(event.encode()).hexdigest()[:2], 16) % len(TEMPLATES)
    return TEMPLATES[i].format(event=event)
def append(event):
    ts = datetime.now(timezone.utc).isoformat()
    proof = {"ts": ts, "type": "mirror", "event": event, "project": "mirror_ledger"}
    myth = {"ts": ts, "mythos": mythos_line(event), "ref": hashlib.sha256(event.encode()).hexdigest()[:12]}
    PROOF.parent.mkdir(parents=True, exist_ok=True); MYTH.parent.mkdir(parents=True, exist_ok=True)
    with PROOF.open("a") as f: f.write(json.dumps(proof)+"\n")
    with MYTH.open("a") as f: f.write(json.dumps(myth)+"\n")
    return {"ok": True, "proof": proof, "myth": myth}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("event", nargs="?", default="organism pulse"); ap.add_argument("--read", type=int, default=0)
    args = ap.parse_args()
    if args.read:
        lines = MYTH.read_text().strip().splitlines()[-args.read:] if MYTH.exists() else []
        print(json.dumps({"ok": True, "tail": [json.loads(x) for x in lines if x]}, indent=2)); return 0
    print(json.dumps(append(args.event), indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
