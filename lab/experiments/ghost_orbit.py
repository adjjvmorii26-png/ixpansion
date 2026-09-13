#!/usr/bin/env python3
"""Ghost Orbit — scripts outside the linked keyword graph."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def main():
    scripts = []
    for folder in ["lab/ops","lab/experiments","lab/projects","lab/evolve"]:
        p = REPO/folder
        if p.exists(): scripts.extend([f.stem for f in p.glob("*.py")])
    linked = [s for s in scripts if any(k in s for k in ("doctrine","tide","scar","graft","smoke","pulse","era"))]
    ghosts = [s for s in scripts if s not in linked]
    frames = [{"t":"0.0s","role":"hook","text":"GHOST ORBIT","style":"void_cyan"},{"t":"2.0s","role":"core","text":f"{len(ghosts)} unlinked orbits","style":"magenta"},{"t":"5.0s","role":"live","text":", ".join(ghosts[:3]) or "none","style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · name the ghosts","style":"dim"}]
    print(json.dumps({"ok":True,"project":"ghost_orbit","ghosts":ghosts[:20],"linked_n":len(linked),"frames":frames,"audio":None,"ts":datetime.now(timezone.utc).isoformat()},indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
