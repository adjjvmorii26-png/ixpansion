#!/usr/bin/env python3
"""Caption Splice — merge two silent packs into one 8s arc."""
from __future__ import annotations
import json
from datetime import datetime, timezone
def main():
    frames = [{"t":"0.0s","role":"hook","text":"SPLICE A","style":"void_cyan"},{"t":"2.0s","role":"core","text":"proof","style":"magenta"},{"t":"5.0s","role":"live","text":"silence","style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · spliced","style":"dim"}]
    print(json.dumps({"ok":True,"project":"caption_splice","frames":frames,"audio":None,"n":len(frames),"ts":datetime.now(timezone.utc).isoformat()},indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
