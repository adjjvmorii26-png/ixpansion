#!/usr/bin/env python3
"""Morse Ledger — phrase → morse for silent captions."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
M = {**{c: v for c, v in zip("abcdefghijklmnopqrstuvwxyz", [".-","-...","-.-.","-..",".","..-.","--.","....","..",".---","-.",".-..","--","-.","---",".--.","--.-",".-.","...","-","..-","...-",".--","-..-","-.--","--.."])}, " ": "/"}
def encode(s: str) -> str:
    return " ".join(M.get(ch, "?") for ch in s.lower() if ch in M or ch == " ")
def main():
    text = " ".join(sys.argv[1:]) or "ix"
    code = encode(text)[:80]
    frames = [{"t":"0.0s","role":"hook","text":"MORSE LEDGER","style":"void_cyan"},{"t":"2.0s","role":"core","text":text[:36],"style":"magenta"},{"t":"5.0s","role":"live","text":code[:42],"style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · silence still speaks","style":"dim"}]
    print(json.dumps({"ok": True, "project": "morse_ledger", "text": text, "morse": code, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
