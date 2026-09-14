#!/usr/bin/env python3
"""Seed Calendar — day-of-year picks today's seed metaphor."""
from __future__ import annotations
import json
from datetime import datetime, timezone
SEEDS = ["Mercy Protocol", "Shared Silence", "Fold Archive", "Epoch Weather", "Spec Gravity", "Refusal Garden", "Quine Pulse", "Bitfield Sky", "Tiny VM", "Palimpsest", "Compass Rose", "Echo Distance"]
def main():
    now = datetime.now(timezone.utc)
    idx = now.timetuple().tm_yday % len(SEEDS)
    title = SEEDS[idx]
    frames = [{"t": "0.0s", "role": "hook", "text": "SEED CALENDAR", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": title, "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"day {now.timetuple().tm_yday}", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · today's seed", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "seed_calendar", "day": now.timetuple().tm_yday, "title": title, "frames": frames, "audio": None, "ts": now.isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
