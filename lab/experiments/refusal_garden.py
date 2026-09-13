#!/usr/bin/env python3
"""Refusal Garden — explicit non-goals as architecture."""
from __future__ import annotations
import json
from datetime import datetime, timezone
REFUSALS = ["merge stale lab tips that delete CI", "tokenized hype without proof transcripts", "dashboard addiction over reading rooms", "silent epoch drift without ceremony", "stock audio on @CoodingLooop doctrine packs"]
def main():
    frames = [{"t": "0.0s", "role": "hook", "text": "REFUSAL GARDEN", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": REFUSALS[0][:42], "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"{len(REFUSALS)} planted refusals", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · what we will not grow", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "refusal_garden", "refusals": REFUSALS, "frames": frames, "audio": None, "doctrine": "refusal is architecture", "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
