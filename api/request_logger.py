"""Request Logger — structured logging for all API requests.

Logs every request with method, path, status, latency, and user.
Supports filtering, export, and analytics.
"""
from __future__ import annotations

import hashlib
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class RequestLogger:
    def __init__(self, max_entries: int = 5000):
        self.max_entries = max_entries
        self.entries: List[Dict] = []

    def log(self, method: str, path: str, status: int, latency_ms: float, user: str = "anonymous") -> Dict:
        entry = {
            "request_id": hashlib.sha256(f"{method}:{path}:{time.time()}".encode()).hexdigest()[:10],
            "method": method, "path": path, "status": status,
            "latency_ms": round(latency_ms, 2), "user": user,
            "timestamp": time.time(),
        }
        self.entries.append(entry)
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        return entry

    def query(self, method: str = None, path: str = None, status: int = None, limit: int = 50) -> List[Dict]:
        results = self.entries
        if method:
            results = [e for e in results if e["method"] == method]
        if path:
            results = [e for e in results if path in e["path"]]
        if status:
            results = [e for e in results if e["status"] == status]
        return results[-limit:]

    def stats(self) -> Dict:
        if not self.entries:
            return {"total": 0}
        latencies = [e["latency_ms"] for e in self.entries]
        statuses = {}
        for e in self.entries:
            s = e["status"]
            statuses[s] = statuses.get(s, 0) + 1
        return {
            "total": len(self.entries),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
            "status_codes": statuses,
        }


def handler(request, response):
    rl = RequestLogger()
    return rl.stats()


def demo():
    rl = RequestLogger()
    print("=== Request Logger ===")
    rl.log("GET", "/api/health", 200, 12.5, "user_1")
    rl.log("POST", "/api/agents/rent", 201, 45.2, "user_2")
    rl.log("GET", "/api/experiments", 200, 8.1, "user_1")
    rl.log("POST", "/api/agents/rent", 500, 120.0, "user_3")
    print(f"\n  Stats: {rl.stats()}")
    errors = rl.query(status=500)
    print(f"  Errors: {len(errors)}")
    return rl.stats()


if __name__ == "__main__":
    demo()
