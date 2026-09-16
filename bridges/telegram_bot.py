"""TelegramBot — bridge to Telegram bot for organism notifications.

Sends alerts, mood updates, and diagnostic summaries to configured chat.
Uses the TELEGRAM_BOT_TOKEN from environment.
"""

from __future__ import annotations

import os
import json
import asyncio
from pathlib import Path
from typing import Any, Optional

try:
    from telebot import TeleBot, types
except ImportError:
    TeleBot = None
    types = None


class TelegramBot:
    """Telegram bridge for organism notifications."""

    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None) -> None:
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "@adjjvmorii")
        self.bot: Optional[TeleBot] = None

        if self.token and TeleBot:
            self.bot = TeleBot(self.token)
            print(f"TelegramBot initialized with chat_id={self.chat_id}")

    def _send_message(self, message: str) -> bool:
        """Send a message to the configured chat."""
        if not self.bot:
            print(f"[Telegram would send]: {message[:100]}")
            return False

        try:
            # Try to send simple text message
            if self.chat_id.startswith("@"):
                # Channel/supergroup
                self.bot.send_message(self.chat_id, message)
            else:
                # Private chat
                self.bot.send_message(self.chat_id, message)
            return True
        except Exception as e:
            print(f"Telegram send error: {e}")
            return False

    def alert(self, title: str, message: str, level: str = "info") -> bool:
        """Send an alert to Telegram with formatting."""
        emoji = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "success": "✅"}
        em = emoji.get(level, "ℹ️")
        message = f"{em} *{title}*\n{message}"
        return self._send_message(message)

    def mood_update(self, state: dict[str, Any]) -> bool:
        """Send organism mood state to Telegram."""
        parts = [f"*Organism Mood*"]
        for key, val in state.items():
            parts.append(f"• {key}: {val}")
        return self._send_message("\n".join(parts))

    def diagnostic_summary(self, title: str, metrics: dict[str, Any]) -> bool:
        """Send diagnostic summary."""
        lines = [f"*{title}*"]
        for k, v in metrics.items():
            lines.append(f"`{k}`: `{v}`")
        return self._send_message("\n".join(lines))

    def wave_update(self, wave_num: int, status: str, details: str = "") -> bool:
        """Send wave progression update."""
        message = f"*Wave {wave_num}*\nStatus: {status}"
        if details:
            message += f"\n{details}"
        return self._send_message(message)


# Singleton instance for easy importing
def get_bot() -> TelegramBot:
    """Get or create the Telegram bot instance."""
    return TelegramBot()


# Convenience functions
def alert(title: str, message: str, level: str = "info") -> bool:
    """Quick alert function."""
    return get_bot().alert(title, message, level)


def mood_update(state: dict[str, Any]) -> bool:
    """Quick mood update function."""
    return get_bot().mood_update(state)


def diagnostic_summary(title: str, metrics: dict[str, Any]) -> bool:
    """Quick diagnostic summary function."""
    return get_bot().diagnostic_summary(title, metrics)
