#!/usr/bin/env python3
"""Glyph Weather — mood + tide → day's weather glyph."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
OPS = Path(__file__).resolve().parent
GLYPHS = {("void","ebb"):"◌",("void","rising"):"◉",("cyan","ebb"):"◈",("cyan","rising"):"✦",("magenta","ebb"):"◇",("magenta","rising"):"✧",("ember","ebb"):"▴",("ember","rising"):"★",("ice","ebb"):"⬡",("ice","rising"):"⬢",("dim","ebb"):"·",("dim","rising"):"∙"}
def jrun(script):
    r = subprocess.run([sys.executable, str(OPS / script)], capture_output=True, text=True, timeout=60)
    try: return json.loads(r.stdout or "{}")
    except json.JSONDecodeError: return {}
def main():
    mood = {}
    mm = REPO / "lab" / "merkle_mood" / "mood.py"
    if mm.exists():
        r = subprocess.run([sys.executable, str(mm)], capture_output=True, text=True, timeout=30)
        try: mood = json.loads(r.stdout or "{}")
        except json.JSONDecodeError: pass
    tide = jrun("proof_tide.py")
    m = mood.get("mood", "void"); phase = tide.get("phase", "ebb")
    glyph = GLYPHS.get((m, phase), "·")
    frames = [{"t":"0.0s","role":"hook","text":f"WEATHER {glyph}","style":"void_cyan"},{"t":"2.5s","role":"core","text":f"{m} · {phase}","style":"magenta"},{"t":"5.5s","role":"live","text":f"glyph {glyph} · tide {tide.get('level',0)}","style":"cyan"},{"t":"8.5s","role":"cta","text":"@CoodingLooop · read the sky not the feed","style":"dim"}]
    out = {"ok": True, "project": "glyph_weather", "glyph": glyph, "mood": m, "phase": phase, "frames": frames, "audio": None, "doctrine": "weather is proof-shaped", "ts": datetime.now(timezone.utc).isoformat()}
    dest = REPO / "content_output" / "captions"; dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"weather_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"
    path.write_text(json.dumps({"ok": True, "frames": frames, "audio": None}, indent=2) + "\n"); out["wrote"] = str(path)
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
