#!/usr/bin/env python3
"""Wave Census — count api/wave* and test_wave*."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def main():
    tests = sorted(p.name for p in (REPO/"tests").glob("test_wave*.py")) if (REPO/"tests").exists() else []
    apis = sorted(p.name for p in (REPO/"api").glob("wave*.py")) if (REPO/"api").exists() else []
    frames = [{"t":"0.0s","role":"hook","text":"WAVE CENSUS","style":"void_cyan"},{"t":"2.0s","role":"core","text":f"{len(apis)} api · {len(tests)} tests","style":"magenta"},{"t":"5.0s","role":"live","text":(apis[-1] if apis else "none")[:40],"style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · know the frontier","style":"dim"}]
    print(json.dumps({"ok":True,"project":"wave_census","api_n":len(apis),"test_n":len(tests),"apis_tail":apis[-5:],"tests_tail":tests[-5:],"frames":frames,"audio":None,"ts":datetime.now(timezone.utc).isoformat()},indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
