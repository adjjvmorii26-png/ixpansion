#!/usr/bin/env python3
"""Resonant Hash Choir — path → 3-note silent chord."""
from __future__ import annotations
import json, hashlib, sys
from datetime import datetime, timezone
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
OCT = ["2", "3", "4", "5"]
def chord(s: str):
    h = hashlib.sha256(s.encode()).digest()
    return [f"{NOTES[h[i] % 12]}{OCT[h[i+3] % 4]}" for i in range(3)]
def main():
    seed = " ".join(sys.argv[1:]) or "lab/experiments/altar_bundle.hexsrc"
    notes = chord(seed)
    frames = [{"t": "0.0s", "role": "hook", "text": "HASH CHOIR", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": " · ".join(notes), "style": "magenta"}, {"t": "5.0s", "role": "live", "text": seed.split("/")[-1][:36], "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · hear without audio", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "resonant_hash_choir", "seed": seed, "chord": notes, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
