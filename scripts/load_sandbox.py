#!/usr/bin/env python3
"""Load .env.sandbox keys into the environment.

Usage:
    eval $(python3 scripts/load_sandbox.py)
    python3 scripts/load_sandbox.py --shell   # print export statements
    python3 scripts/load_sandbox.py --json    # print as JSON
    python3 scripts/load_sandbox.py --check   # verify keys exist
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SANDBOX_ENV = ROOT / ".env.sandbox"
PROD_ENV = ROOT / ".env"


def load_env_file(path: Path) -> dict:
    """Parse a .env file into a dict."""
    env = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--shell"

    sandbox = load_env_file(SANDBOX_ENV)
    prod = load_env_file(PROD_ENV)

    if not sandbox:
        print("ERROR: .env.sandbox not found. Run: cp .env.sandbox.example .env.sandbox", file=sys.stderr)
        sys.exit(1)

    # Merge: sandbox overrides prod for SANDBOX_* keys, prod is fallback
    merged = {**prod, **sandbox}

    if mode == "--check":
        required = [
            "SANDBOX_OPENAI_KEY", "SANDBOX_VERCEL_TOKEN", "SANDBOX_TELEGRAM_TOKEN",
        ]
        missing = [k for k in required if not merged.get(k) or "your-" in merged.get(k, "")]
        if missing:
            print(f"MISSING: {', '.join(missing)}")
            sys.exit(1)
        else:
            print(f"OK: {len(required)} required keys present")
            print(f"Sandbox ID: {merged.get('SANDBOX_ID', 'unknown')}")
            print(f"Total keys: {len(sandbox)}")
            sys.exit(0)

    elif mode == "--json":
        safe = {k: v for k, v in merged.items() if "KEY" in k or "TOKEN" in k}
        safe["_sanitized"] = True
        safe["_count"] = len(merged)
        print(json.dumps(safe, indent=2))

    else:
        # Shell export mode
        for key, value in sorted(merged.items()):
            print(f'export {key}="{value}"')


if __name__ == "__main__":
    main()
