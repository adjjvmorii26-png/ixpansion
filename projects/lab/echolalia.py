#!/usr/bin/env python3
"""Echolalia mutates one phrase through bounded generations and keeps every voice."""
from __future__ import annotations
import argparse, hashlib, json

OPERATIONS = ["reverse", "title", "whisper", "expand"]


def echo(phrase: str, generations: int = 5) -> dict:
    if not phrase.strip() or generations < 1:
        raise ValueError("phrase and positive generations are required")
    voices = [{"generation": 0, "text": phrase}]
    current = phrase
    for generation in range(1, generations + 1):
        operation = OPERATIONS[(generation + len(phrase)) % len(OPERATIONS)]
        if operation == "reverse":
            current = current[::-1]
        elif operation == "title":
            current = current.title()
        elif operation == "whisper":
            current = current.lower() + "…"
        else:
            current = f"{current} {current[-1] * 2}"
        voices.append({"generation": generation, "operation": operation, "text": current})
    return {"voices": voices, "final": current, "signature": hashlib.sha256(current.encode()).hexdigest()[:20]}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--phrase", default="the lattice listens")
    parser.add_argument("--generations", type=int, default=5)
    args = parser.parse_args(argv)
    try: print(json.dumps(echo(args.phrase, args.generations), sort_keys=True))
    except ValueError as error: print(json.dumps({"ok": False, "error": str(error)})); return 1
    return 0


if __name__ == "__main__": raise SystemExit(main())
