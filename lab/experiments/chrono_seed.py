#!/usr/bin/env python3
"""Chrono Seed — future-wave ideas with lock hashes."""
from __future__ import annotations
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
SEED_FILE = REPO / "lab" / "experiments" / "chrono_seeds.json"
IDEAS = [{"wave": 460, "title": "Mercy Protocol", "blurb": "organs that can refuse harmful tasks"}, {"wave": 470, "title": "Shared Silence", "blurb": "multi-reader caption wells"}, {"wave": 480, "title": "Fold Archive", "blurb": "collapse 100 waves into 10 denser organs"}]
def main():
    state = {"seeds": []}
    if SEED_FILE.exists():
        try: state = json.loads(SEED_FILE.read_text())
        except json.JSONDecodeError: pass
    for idea in IDEAS:
        lock = hashlib.sha256(f"{idea['wave']}:{idea['title']}".encode()).hexdigest()[:12]
        state.setdefault("seeds", []).append({**idea, "lock": lock, "planted": datetime.now(timezone.utc).isoformat()})
    state["seeds"] = state["seeds"][-30:]
    SEED_FILE.write_text(json.dumps(state, indent=2)+"\n")
    frames = [{"t":"0.0s","role":"hook","text":"CHRONO SEED","style":"void_cyan"},{"t":"2.0s","role":"core","text":IDEAS[0]["title"],"style":"magenta"},{"t":"5.0s","role":"live","text":f"wave {IDEAS[0]['wave']} locked","style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · plant the future","style":"dim"}]
    print(json.dumps({"ok":True,"project":"chrono_seed","n":len(state["seeds"]),"frames":frames,"audio":None,"ts":datetime.now(timezone.utc).isoformat()},indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
