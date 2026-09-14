#!/usr/bin/env python3
"""Tiny VM — 8-op stack machine → 16-bit badge."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
def run(program, stack=None):
    stack = list(stack or []); i = 0; steps = 0
    while i < len(program) and steps < 64:
        op = program[i]; steps += 1
        if op == "PUSH":
            i += 1; stack.append(int(program[i]) & 0xFFFF)
        elif op == "XOR" and len(stack) >= 2:
            b, a = stack.pop(), stack.pop(); stack.append((a ^ b) & 0xFFFF)
        elif op == "ADD" and len(stack) >= 2:
            b, a = stack.pop(), stack.pop(); stack.append((a + b) & 0xFFFF)
        elif op == "DUP" and stack: stack.append(stack[-1])
        elif op == "POP" and stack: stack.pop()
        elif op == "HALT": break
        i += 1
    return stack
def badge(text: str) -> int:
    program = []
    for ch in text[:32]:
        program += ["PUSH", str(ord(ch)), "XOR"] if program else ["PUSH", str(ord(ch))]
    program += ["DUP", "ADD", "HALT"]
    st = run(program)
    return st[-1] if st else 0
def main():
    text = " ".join(sys.argv[1:]) or "IXPANSION"
    b = badge(text)
    frames = [{"t": "0.0s", "role": "hook", "text": "TINY VM", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"badge 0x{b:04x}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": text[:36], "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · small machines tell truth", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "tiny_vm", "input": text, "badge": b, "badge_hex": f"0x{b:04x}", "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
