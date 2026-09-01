#!/usr/bin/env python3
"""Send an IXpansion organism update to Telegram.

Uses the same config as the telegraph skill: ~/.codex/telegram-bridge.json
{ "botToken": "...", "chatIds": [123] }
or environment VERCEL_TELEGRAM_TOKEN / VERCEL_TELEGRAM_CHAT.

Usage:
  python3 tools/broadcast/send_organism_update.py --event wave_birth --wave 213
  python3 tools/broadcast/send_organism_update.py --message "Custom text"
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

CONFIG_PATH = os.path.expanduser("~/.codex/telegram-bridge.json")


def _load_config() -> tuple:
    token = os.environ.get("VERCEL_TELEGRAM_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("VERCEL_TELEGRAM_CHAT") or os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat:
        return token, [int(chat)]
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload.get("botToken"), payload.get("chatIds") or []
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return None, []


def main():
    parser = argparse.ArgumentParser(description="Send IXpansion update to Telegram")
    parser.add_argument("--message", help="Raw message text")
    parser.add_argument("--event", default="state_pulse", help="Event type")
    parser.add_argument("--wave", default=213, type=int)
    parser.add_argument("--wave-name", default="The Organism Emits")
    parser.add_argument("--living", default=302, type=int)
    args = parser.parse_args()

    token, chat_ids = _load_config()
    if not token:
        print("No token configured. Set VERCEL_TELEGRAM_TOKEN+CHAT or ~/.codex/telegram-bridge.json")
        sys.exit(1)
    chat_id = chat_ids[0] if chat_ids else None
    if not chat_id:
        print("No chat id configured. Send /start to your bot and add chatIds.")
        sys.exit(1)

    text = args.message or (
        f"\U0001F30C IXPANSION · Wave {args.wave} · {args.wave_name}\n"
        f"Event: {args.event}\nLiving modules: {args.living}"
    )
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    print("ok" if result.get("ok") else result)


if __name__ == "__main__":
    main()
