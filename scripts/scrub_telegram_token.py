#!/usr/bin/env python3
"""Scrub hardcoded TELEGRAM_BOT_TOKEN defaults from api/aleph_bot.py"""
import re, sys
from pathlib import Path
p = Path(sys.argv[1] if len(sys.argv) > 1 else "api/aleph_bot.py")
t = p.read_text()
t2 = re.sub(
    r'BOT_TOKEN\s*=\s*os\.environ\.get\(\s*"TELEGRAM_BOT_TOKEN"\s*,\s*"[^"]*"\s*\)',
    'BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()',
    t,
)
t2 = re.sub(
    r'os\.environ\.get\("TELEGRAM_BOT_TOKEN",\s*"[0-9]+:[^"]+"\)',
    'os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()',
    t2,
)
if '"token": BOT_TOKEN' in t2:
    t2 = t2.replace('"token": BOT_TOKEN', '"token_set": bool(BOT_TOKEN)')
if t2 == t:
    print("no changes needed")
else:
    p.write_text(t2)
    print("scrubbed", p)
