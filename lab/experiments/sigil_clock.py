#!/usr/bin/env python3
"""Sigil Clock — UTC hour → 4-glyph sigil."""
from __future__ import annotations
import json
from datetime import datetime, timezone
GLYPHS = "◇◆○●△▲□■☆★✦✧"
def main():
    h = datetime.now(timezone.utc).hour
    sig = "".join(GLYPHS[(h + i * 3) % len(GLYPHS)] for i in range(4))
    frames = [{"t":"0.0s","role":"hook","text":"SIGIL CLOCK","style":"void_cyan"},{"t":"2.0s","role":"core","text":sig,"style":"magenta"},{"t":"5.0s","role":"live","text":f"hour {h} UTC","style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · time as mark","style":"dim"}]
    print(json.dumps({"ok":True,"project":"sigil_clock","hour":h,"sigil":sig,"frames":frames,"audio":None,"ts":datetime.now(timezone.utc).isoformat()},indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
