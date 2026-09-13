#!/usr/bin/env python3
"""Dream Residue — almost-organs as vectors."""
from __future__ import annotations
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
RES = REPO / "lab" / "experiments" / "dream_residue.json"
SEEDS = ["gravity of unread logs", "CHRONOFORGE epoch ceremony", "soft eclipse of failed deploys", "mirror of absences", "clock that ticks on proof"]
def vec(s):
    h = hashlib.sha256(s.encode()).hexdigest()
    return [int(h[i:i+2], 16)/255 for i in range(0, 16, 2)]
def main():
    state = {"residues": []}
    if RES.exists():
        try: state = json.loads(RES.read_text())
        except json.JSONDecodeError: pass
    for s in SEEDS:
        state.setdefault("residues", []).append({"seed": s, "v": vec(s), "ts": datetime.now(timezone.utc).isoformat()})
    state["residues"] = state["residues"][-40:]
    RES.write_text(json.dumps(state, indent=2)+"\n")
    frames = [{"t":"0.0s","role":"hook","text":"DREAM RESIDUE","style":"void_cyan"},{"t":"2.0s","role":"core","text":f"{len(state['residues'])} almost-organs","style":"magenta"},{"t":"5.0s","role":"live","text":SEEDS[1][:40],"style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · keep the almosts","style":"dim"}]
    print(json.dumps({"ok":True,"project":"dream_residue","n":len(state["residues"]),"frames":frames,"audio":None,"ts":datetime.now(timezone.utc).isoformat()},indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
