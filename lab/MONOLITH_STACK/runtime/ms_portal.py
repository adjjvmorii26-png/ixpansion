#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
MS = ROOT.parent
def main():
    act = (sys.argv[1] if len(sys.argv)>1 else "help").lower()
    if act in ("help","-h","--help"):
        print(json.dumps({"acts":["glyphs","vm","epochs","boot","ethics"]}, indent=2)); return 0
    if act=="glyphs":
        r=subprocess.run([sys.executable,str(ROOT/"glyph_engine.py")],capture_output=True,text=True)
        print(r.stdout or r.stderr); return r.returncode
    if act=="vm":
        r=subprocess.run([sys.executable,str(MS/"REBUILD_KERNEL"/"reference_interpreter"/"python"/"interp.py")],capture_output=True,text=True)
        print(r.stdout or r.stderr); return r.returncode
    if act=="epochs":
        arcs=sorted((MS/"CRYPT_ARCHIVE").glob("EPOCH_*"))
        print(json.dumps({"epochs":[p.name for p in arcs],"n":len(arcs)},indent=2)); return 0
    if act=="ethics":
        ok=(MS/"PRIME_CORE"/"PRIME_GLYPHS.hex").exists()
        print(json.dumps({"ok":ok,"issues":[] if ok else ["glyphs_missing"],"mandatory":True},indent=2))
        return 0 if ok else 1
    if act=="boot":
        steps=[]; ok=True
        for name in ("ethics","glyphs","vm"):
            r=subprocess.run([sys.executable,str(ROOT/"ms_portal.py"),name],capture_output=True,text=True)
            steps.append({"step":name,"ok":r.returncode==0}); ok&=r.returncode==0
        print(json.dumps({"boot":True,"ok":ok,"steps":steps},indent=2)); return 0 if ok else 1
    print(json.dumps({"ok":False,"err":"unknown"})); return 1
if __name__=="__main__":
    raise SystemExit(main())
