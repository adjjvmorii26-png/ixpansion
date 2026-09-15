#!/usr/bin/env python3
"""Entropy Meter — Shannon entropy of a lab file."""
from __future__ import annotations
import json, math, sys
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter
REPO = Path(__file__).resolve().parents[2]
def entropy(data: bytes) -> float:
    if not data: return 0.0
    c, n = Counter(data), len(data)
    return -sum((v/n) * math.log2(v/n) for v in c.values())
def main():
    p = Path(sys.argv[1]) if len(sys.argv)>1 else REPO/"lab"/"experiments"/"consent_registry.json"
    if not p.is_absolute(): p = REPO/p
    data = p.read_bytes() if p.exists() else b""
    e = round(entropy(data), 4)
    frames = [{"t":"0.0s","role":"hook","text":"ENTROPY METER","style":"void_cyan"},{"t":"2.0s","role":"core","text":f"H={e}","style":"magenta"},{"t":"5.0s","role":"live","text":p.name,"style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · measure the mess","style":"dim"}]
    print(json.dumps({"ok":True,"project":"entropy_meter","path":str(p),"entropy":e,"bytes":len(data),"frames":frames,"audio":None,"ts":datetime.now(timezone.utc).isoformat()},indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
