#!/usr/bin/env python3
"""Listen across Project labs and classify the combined silence or signal."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LABS=[ROOT/"projects/lab/echolalia.py",ROOT/"projects/lab/schism.py",ROOT/"projects/lab/tide_clock.py",ROOT/"projects/lab/interloper.py"]


def listen(verbose=False):
    signals=[]
    for script in LABS:
        result=subprocess.run([sys.executable,str(script)],capture_output=True,text=True,check=False)
        try: payload=json.loads(result.stdout)
        except json.JSONDecodeError: payload=result.stdout.strip()
        signals.append({"source":str(script.relative_to(ROOT)),"ok":result.returncode==0,"signal":payload})
    entropy=sum(1 for item in signals if item["ok"])
    return {"listening_post":{"channels":len(signals),"healthy":entropy,"state":"receiving" if entropy else "silent"},"signals":signals}


def main(argv=None):
    parser=argparse.ArgumentParser(); parser.add_argument("--verbose",action="store_true"); args=parser.parse_args(argv)
    print(json.dumps(listen(args.verbose),sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
