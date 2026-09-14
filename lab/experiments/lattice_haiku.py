#!/usr/bin/env python3
"""Lattice Haiku — lab tree counts as 5-7-5."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def count(p):
    path = REPO/p
    return len(list(path.rglob("*.py"))) if path.exists() else 0
def main():
    ops, exp, cf = count("lab/ops"), count("lab/experiments"), count("lab/CHRONOFORGE")
    l1, l2, l3 = f"{cf} forge lines", "experiments unfold slow quiet code", f"{ops} ops wait"
    print(json.dumps({"ok":True,"project":"lattice_haiku","haiku":f"{l1}\n{l2}\n{l3}","counts":{"chronoforge":cf,"experiments":exp,"ops":ops},"frames":[{"t":"0.0s","role":"hook","text":"LATTICE HAIKU","style":"void_cyan"},{"t":"2.0s","role":"core","text":l1,"style":"magenta"},{"t":"5.0s","role":"live","text":l2[:42],"style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · structure as poem","style":"dim"}],"audio":None,"ts":datetime.now(timezone.utc).isoformat()},indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
