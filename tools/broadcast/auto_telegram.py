#!/usr/bin/env python3
"""Auto-complete the Telegram bridge.

Polls getUpdates until the user has messaged the bot (getting their
chat_id), persists it to ~/.codex/telegram-bridge.json, then drains the
pending broadcast queue (tools/broadcast/pending/*.json) and sends each.

Usage:
  python3 tools/broadcast/auto_telegram.py              # one poll cycle
  python3 tools/broadcast/auto_telegram.py --wait 300   # poll every 5s for 300s
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.request
from pathlib import Path

CONFIG_PATH = Path.home() / ".codex" / "telegram-bridge.json"
PENDING_DIR = Path(__file__).resolve().parent / "pending"
TOKEN = os.environ.get("VERCEL_TELEGRAM_TOKEN") or "8903755459:AAFl6i9cbI-lFEvoHcK3OhyBWWGetg4V0Ss"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {"botToken": TOKEN, "chatIds": []}


def save_config(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))
    os.chmod(CONFIG_PATH, 0o600)


def api(method: str, data: dict) -> dict:
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def discover_chat_id(cfg: dict) -> int | None:
    if cfg.get("chatIds"):
        return cfg["chatIds"][0]
    result = api("getUpdates", {"limit": 20, "allowed_updates": ["message"], "timeout": 2})
    for update in reversed(result.get("result", [])):
        msg = update.get("message", {})
        chat = msg.get("chat", {})
        if isinstance(chat.get("id"), int):
            return chat["id"]
    return None


def send_pending(chat_id: int) -> list:
    sent = []
    if not PENDING_DIR.exists():
        return sent
    for f in sorted(PENDING_DIR.glob("*.json")):
        try:
            item = json.loads(f.read_text())
            result = api("sendMessage", {"chat_id": chat_id, "text": item.get("text", "")})
            sent.append({"file": f.name, "ok": result.get("ok")})
            f.unlink()  # drain the queue
        except Exception as exc:  # noqa: BLE001
            sent.append({"file": f.name, "ok": False, "error": str(exc)})
    return sent


def main():
    parser = argparse.ArgumentParser(description="Auto-complete the Telegram bridge")
    parser.add_argument("--wait", type=int, default=0, help="total seconds to keep polling (0 = one shot)")
    args = parser.parse_args()

    deadline = time.time() + args.wait
    while True:
        cfg = load_config()
        chat_id = discover_chat_id(cfg)
        if chat_id:
            cfg["chatIds"] = [chat_id]
            save_config(cfg)
            print(f"CHAT_ID_DISCOVERED={chat_id}")
            sent = send_pending(chat_id)
            print(f"PENDING_SENT={len(sent)} {sent}")
            return
        if time.time() >= deadline:
            print("NO_CHAT_ID_YET — user must message @alpeha_bot first")
            return
        time.sleep(5)


if __name__ == "__main__":
    main()
