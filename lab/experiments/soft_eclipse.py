#!/usr/bin/env python3
"""Soft Eclipse — bright organs occult dimmer ones."""
from __future__ import annotations
import json, hashlib
from datetime import datetime, timezone
ORGS = ["cartography","weather","paradox","homestead","mycelial","lab_smoke","doctrine"]
def mass(name):
    return (int(hashlib.sha256(name.encode()).hexdigest()[:4],16) % 100) / 100.0
def main():
    ranked = sorted(((o, mass(o)) for o in ORGS), key=lambda x: -x[1])
    occulted = [o for o,m in ranked[3:]]
    frames = [{"t":"0.0s","role":"hook","text":"SOFT ECLIPSE","style":"void_cyan"},{"t":"2.0s","role":"core","text":f"bright {ranked[0][0]}","style":"magenta"},{"t":"5.0s","role":"live","text":"occulted: "+", ".join(occulted[:3]),"style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · notice the shadow","style":"dim"}]
    print(json.dumps({"ok":True,"project":"soft_eclipse","ranked":ranked,"occulted":occulted,"frames":frames,"audio":None,"doctrine":"brightness is not truth","ts":datetime.now(timezone.utc).isoformat()},indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
