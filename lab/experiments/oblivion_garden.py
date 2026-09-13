#!/usr/bin/env python3
"""Oblivion Garden — intentional forgetting (TTL tombs catalog)."""
from __future__ import annotations
import json, time
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
GARDEN = REPO / "lab" / "experiments" / "oblivion_state.json"
def main():
    state = {"tombs": []}
    if GARDEN.exists():
        try: state = json.loads(GARDEN.read_text())
        except json.JSONDecodeError: pass
    tombs = state.setdefault("tombs", [])
    tombs.append({"id": f"tomb_{int(time.time())}", "target": "content_output/captions/*_old*", "ttl_sec": 86400 * 30, "planted": datetime.now(timezone.utc).isoformat(), "reason": "intentional_oblivion"})
    tombs[:] = tombs[-30:]
    state["n"] = len(tombs); state["doctrine"] = "forgetting is a feature"
    GARDEN.parent.mkdir(parents=True, exist_ok=True)
    GARDEN.write_text(json.dumps(state, indent=2) + "\n")
    frames = [{"t": "0.0s", "role": "hook", "text": "OBLIVION GARDEN", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"{len(tombs)} tombs planted", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": "forget on purpose", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · memory with edges", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "oblivion_garden", "n_tombs": len(tombs), "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
