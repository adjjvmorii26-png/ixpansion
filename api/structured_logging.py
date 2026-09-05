"""Structured Logging — JSON-formatted log entries with context.

Replaces print-based logging with structured JSON logs that are
machine-readable and searchable. Supports log levels, context
binding, and log aggregation.
"""
from __future__ import annotations

import hashlib
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

LEVELS = {"debug": 0, "info": 1, "warn": 2, "error": 3, "fatal": 4}


class Logger:
    def __init__(self, name: str, min_level: str = "debug"):
        self.name = name
        self.min_level = LEVELS.get(min_level, 0)
        self.entries: List[Dict] = []
        self.context: Dict[str, Any] = {}

    def _log(self, level: str, message: str, extra: Dict = None):
        if LEVELS.get(level, 0) < self.min_level:
            return
        entry = {
            "timestamp": time.time(),
            "level": level,
            "logger": self.name,
            "message": message,
            "context": self.context.copy(),
        }
        if extra:
            entry["extra"] = extra
        self.entries.append(entry)
        return entry

    def bind(self, **kwargs):
        self.context.update(kwargs)
        return self

    def debug(self, message: str, **extra):
        return self._log("debug", message, extra or None)

    def info(self, message: str, **extra):
        return self._log("info", message, extra or None)

    def warn(self, message: str, **extra):
        return self._log("warn", message, extra or None)

    def error(self, message: str, **extra):
        return self._log("error", message, extra or None)

    def fatal(self, message: str, **extra):
        return self._log("fatal", message, extra or None)

    def get_entries(self, level: str = None, limit: int = 50) -> List[Dict]:
        entries = self.entries
        if level:
            entries = [e for e in entries if e["level"] == level]
        return entries[-limit:]

    def stats(self) -> Dict:
        level_counts = {}
        for e in self.entries:
            l = e["level"]
            level_counts[l] = level_counts.get(l, 0) + 1
        return {
            "logger": self.name,
            "total_entries": len(self.entries),
            "level_counts": level_counts,
            "context_keys": list(self.context.keys()),
        }


_loggers: Dict[str, Logger] = {}


def get_logger(name: str, min_level: str = "debug") -> Logger:
    if name not in _loggers:
        _loggers[name] = Logger(name, min_level)
    return _loggers[name]


def handler(request, response):
    return {
        "loggers": list(_loggers.keys()),
        "total_entries": sum(l.stats()["total_entries"] for l in _loggers.values()),
    }


def demo():
    print("=== Structured Logging ===")
    api_log = get_logger("api").bind(module="gateway", request_id="abc123")
    api_log.info("Request received", method="POST", path="/api/agents/rent")
    api_log.info("Agent rented", agent="scout_alpha", hours=2, cost=10.0)
    api_log.warn("Rate limit approaching", current=95, limit=100)
    api_log.error("Payment failed", user="test", reason="insufficient_funds")

    auth_log = get_logger("auth").bind(module="auth")
    auth_log.info("API key validated", tier="pro")
    auth_log.debug("Token refreshed")

    for name, logger in _loggers.items():
        stats = logger.stats()
        print(f"\n  {name}: {stats['total_entries']} entries")
        for level, count in stats["level_counts"].items():
            print(f"    {level}: {count}")

    return handler({}, {})


if __name__ == "__main__":
    demo()

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "0", "module": "structured_logging"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
