"""Telegram aleph_bot Vibe Pulse Broadcasts.
Sends vibe pulses and organism state to Telegram users via aleph_bot."""
import json
import time
import os
import random
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Telegram bot configuration
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8903755459:AAGwjuM6Q5U8lclNO980VfN2Gjtv90WCbMk")

# Vibe pulse emoji mapping
_VIBE_EMOJI = {
    "surge": "🌊",
    "ebb": "🌊",
    "ripple": "🌊",
    "tsunami": "🌊🌊",
    "whisper": "🍃",
    "crescendo": "📈",
    "decay": "🍂",
    "explosion": "💥",
    "stillness": "🧘",
    "pulse": "💓"
}

# Mood emoji mapping
_MOOD_EMOJI = {
    "serene": "😌",
    "stormy": "😡",
    "volatile": "😵",
    "focused": "🤔",
    "drifting": "😐",
    "excited": "🤩",
    "calm": "🧘",
    "anxious": "😟",
    "joyful": "🥳",
    "sad": "😢"
}

# Broadcast state
_broadcast_state = {
    "subscriptions": {},  # chat_id -> {pulse_types, mood_alerts, frequency}
    "broadcasts_sent": 0,
    "last_broadcast": None,
    "broadcast_history": []
}


def _telegram(method: str, params: dict) -> dict:
    """Call Telegram Bot API using stdlib."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = urllib.parse.urlencode(params).encode()
    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode() or "{}")
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def get_chat_ids() -> list:
    """Get registered chat IDs from storage."""
    chat_ids_path = os.path.join(DATA_DIR, "telegram_chat_ids.json")
    try:
        with open(chat_ids_path) as f:
            data = json.load(f)
            return data.get("chat_ids", [])
    except Exception:
        return []


def register_chat_id(chat_id: int) -> dict:
    """Register a chat ID for pulse broadcasts."""
    chat_id = int(chat_id)
    if chat_id < 10000:
        return {"status": "error", "reason": "Invalid chat ID"}
    
    # Add to subscriptions with default settings
    _broadcast_state["subscriptions"][chat_id] = {
        "pulse_types": "all",
        "mood_alerts": True,
        "frequency": "realtime",
        "subscribed_at": time.time()
    }
    
    # Persist to file
    chat_ids_path = os.path.join(DATA_DIR, "telegram_chat_ids.json")
    try:
        existing = {"chat_ids": get_chat_ids()}
        if chat_id not in existing["chat_ids"]:
            existing["chat_ids"].append(chat_id)
            existing["updated"] = time.time()
            with open(chat_ids_path, "w") as f:
                json.dump(existing, f, indent=2)
    except Exception:
        pass
    
    return {
        "status": "subscribed",
        "chat_id": chat_id,
        "settings": _broadcast_state["subscriptions"][chat_id]
    }


def unregister_chat_id(chat_id: int) -> dict:
    """Unregister a chat ID from pulse broadcasts."""
    chat_id = int(chat_id)
    _broadcast_state["subscriptions"].pop(chat_id, None)
    
    # Remove from file
    chat_ids_path = os.path.join(DATA_DIR, "telegram_chat_ids.json")
    try:
        existing = {"chat_ids": get_chat_ids()}
        if chat_id in existing["chat_ids"]:
            existing["chat_ids"].remove(chat_id)
            existing["updated"] = time.time()
            with open(chat_ids_path, "w") as f:
                json.dump(existing, f, indent=2)
    except Exception:
        pass
    
    return {"status": "unsubscribed", "chat_id": chat_id}


def format_vibe_pulse_message(pulse: dict, mood: dict = None) -> str:
    """Format a vibe pulse as a Telegram message."""
    vibe_type = pulse.get("type", "unknown")
    intensity = pulse.get("intensity", 0)
    vector = pulse.get("vector", {})
    age = pulse.get("age", "")
    
    emoji = _VIBE_EMOJI.get(vibe_type, "🌀")
    
    # Build message
    msg = f"{emoji} *Vibe Pulse: {vibe_type.capitalize()}*\n"
    msg += f"📊 Intensity: {intensity:.2f}\n"
    msg += f"⏰ {age}\n\n"
    
    # Add vector summary
    msg += "📈 *Vectors:*\n"
    for key, value in vector.items():
        bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
        msg += f"  {key}: [{bar}] {value:.2f}\n"
    
    # Add mood context
    if mood:
        mood_emoji = _MOOD_EMOJI.get(mood.get("mood", "neutral"), "😐")
        msg += f"\n{mood_emoji} *Mood:* {mood.get('mood', 'neutral')} ({mood.get('intensity', 0):.2f})"
        msg += f"\n💓 *Pulse:* {mood.get('pulse_type', 'stillness')}"
    
    return msg


def send_vibe_pulse(pulse: dict, mood: dict = None, chat_ids: list = None) -> dict:
    """Send vibe pulse to registered Telegram chat IDs."""
    if chat_ids is None:
        chat_ids = get_chat_ids()
    
    if not chat_ids:
        return {"status": "no_recipients", "message": "No chat IDs registered"}
    
    message = format_vibe_pulse_message(pulse, mood)
    sent_count = 0
    failed = []
    
    for chat_id in chat_ids:
        # Check subscription settings
        settings = _broadcast_state["subscriptions"].get(chat_id, {})
        pulse_types = settings.get("pulse_types", "all")
        
        if pulse_types != "all" and pulse.get("type") not in pulse_types:
            continue
        
        result = _telegram("sendMessage", {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        })
        
        if result.get("ok"):
            sent_count += 1
        else:
            failed.append({"chat_id": chat_id, "error": result.get("error")})
    
    # Record broadcast
    broadcast_record = {
        "pulse": pulse,
        "mood": mood,
        "sent_to": sent_count,
        "failed": failed,
        "timestamp": time.time()
    }
    _broadcast_state["broadcasts_sent"] += 1
    _broadcast_state["last_broadcast"] = broadcast_record
    _broadcast_state["broadcast_history"].append(broadcast_record)
    
    if len(_broadcast_state["broadcast_history"]) > 50:
        _broadcast_state["broadcast_history"] = _broadcast_state["broadcast_history"][-50:]
    
    return {
        "status": "sent" if sent_count > 0 else "failed",
        "sent_count": sent_count,
        "failed_count": len(failed),
        "recipients": chat_ids
    }


def send_mood_alert(mood: dict, chat_ids: list = None) -> dict:
    """Send mood change alert to subscribed users."""
    if chat_ids is None:
        chat_ids = get_chat_ids()
    
    # Filter for mood alerts enabled
    subscribed = []
    for cid in chat_ids:
        settings = _broadcast_state["subscriptions"].get(cid, {})
        if settings.get("mood_alerts", True):
            subscribed.append(cid)
    
    if not subscribed:
        return {"status": "no_recipients", "message": "No mood alert subscribers"}
    
    mood_emoji = _MOOD_EMOJI.get(mood.get("mood", "neutral"), "😐")
    message = f"{mood_emoji} *Mood Alert*\n"
    message += f"🌙 *New Mood:* {mood.get('mood', 'unknown').capitalize()}\n"
    message += f"💓 *Intensity:* {mood.get('intensity', 0):.2f}\n"
    message += f"💫 *Pulse Type:* {mood.get('pulse_type', 'stillness')}\n"
    message += f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(mood.get('timestamp', time.time())))}"
    
    sent_count = 0
    for chat_id in subscribed:
        result = _telegram("sendMessage", {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        })
        if result.get("ok"):
            sent_count += 1
    
    return {"status": "sent", "sent_count": sent_count, "recipients": subscribed}


def get_broadcast_status() -> dict:
    """Get current broadcast status."""
    return {
        "subscribers": len(_broadcast_state["subscriptions"]),
        "chat_ids": list(_broadcast_state["subscriptions"].keys()),
        "broadcasts_sent": _broadcast_state["broadcasts_sent"],
        "last_broadcast": _broadcast_state["last_broadcast"],
        "history_count": len(_broadcast_state["broadcast_history"])
    }


# CLI entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Telegram Vibe Pulse Broadcasts")
    parser.add_argument("--register", type=int, help="Register chat ID")
    parser.add_argument("--unregister", type=int, help="Unregister chat ID")
    parser.add_argument("--pulse", action="store_true", help="Send test pulse")
    parser.add_argument("--mood", action="store_true", help="Send mood alert")
    parser.add_argument("--status", action="store_true", help="Show broadcast status")
    
    args = parser.parse_args()
    
    if args.register:
        result = register_chat_id(args.register)
        print(f"Register: {json.dumps(result)}")
    
    if args.unregister:
        result = unregister_chat_id(args.unregister)
        print(f"Unregister: {json.dumps(result)}")
    
    if args.pulse:
        from api.vibebot import generate_vibe_pulse
        from api.organism_mood import get_current_mood
        pulse = generate_vibe_pulse()
        mood = get_current_mood()
        result = send_vibe_pulse(pulse, mood)
        print(f"Pulse sent: {json.dumps(result)}")
    
    if args.mood:
        from api.organism_mood import get_current_mood
        mood = get_current_mood()
        result = send_mood_alert(mood)
        print(f"Mood alert: {json.dumps(result)}")
    
    if args.status:
        result = get_broadcast_status()
        print(f"Status: {json.dumps(result)}")
    
    if not any([args.register, args.unregister, args.pulse, args.mood, args.status]):
        print("Telegram Vibe Pulse Broadcasts operational")
        print("Commands: --register <chat_id>, --unregister <chat_id>")
        print("          --pulse, --mood, --status")
