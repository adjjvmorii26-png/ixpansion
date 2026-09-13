#!/usr/bin/env python3
"""Spec Gravity — docs as gravitational bodies (bytes × keyword mass)."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
KEYS = ("invariant", "epoch", "ethics", "charter", "testament", "doctrine")
def main():
    scores = []
    for base in [REPO / "lab" / "CHRONOFORGE", REPO / "lab" / "STRATUM_ENGINE", REPO / "docs"]:
        if not base.exists(): continue
        for f in base.rglob("*"):
            if f.suffix.lower() not in {".md", ".hex", ".yaml", ".yml", ".json"}: continue
            try: text = f.read_text(errors="ignore")
            except OSError: continue
            mass = sum(text.lower().count(k) for k in KEYS)
            scores.append({"path": str(f.relative_to(REPO)), "pull": len(text) * (1 + mass), "mass": mass})
    scores.sort(key=lambda x: -x["pull"]); top = scores[:5]
    frames = [{"t": "0.0s", "role": "hook", "text": "SPEC GRAVITY", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": (top[0]["path"][-40:] if top else "none"), "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"{len(scores)} bodies measured", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · orbit the heavy specs", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "spec_gravity", "top": top, "n": len(scores), "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
