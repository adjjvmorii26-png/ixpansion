"""Rate Limiter — token bucket rate limiting per user/service.

Prevents abuse by limiting request rates. Uses token bucket algorithm
for smooth rate limiting with burst support.
"""
from __future__ import annotations

import json
import time
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class RateLimiter:
    def __init__(self, default_rate: int = 100, default_burst: int = 20):
        self.default_rate = default_rate
        self.default_burst = default_burst
        self.buckets: Dict[str, Dict] = {}

    def _get_bucket(self, key: str, rate: int = None, burst: int = None) -> Dict:
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens": burst or self.default_burst,
                "max_tokens": burst or self.default_burst,
                "rate": rate or self.default_rate,
                "last_refill": time.time(),
            }
        bucket = self.buckets[key]
        elapsed = time.time() - bucket["last_refill"]
        refill = elapsed * (bucket["rate"] / 60)
        bucket["tokens"] = min(bucket["max_tokens"], bucket["tokens"] + refill)
        bucket["last_refill"] = time.time()
        return bucket

    def allow(self, key: str, tokens: int = 1) -> Dict:
        bucket = self._get_bucket(key)
        if bucket["tokens"] >= tokens:
            bucket["tokens"] -= tokens
            return {"allowed": True, "remaining": int(bucket["tokens"])}
        return {"allowed": False, "remaining": int(bucket["tokens"]), "retry_after": round((tokens - bucket["tokens"]) / (bucket["rate"] / 60), 2)}

    def status(self, key: str = None) -> Dict:
        if key:
            bucket = self._get_bucket(key)
            return {"tokens": int(bucket["tokens"]), "max": bucket["max_tokens"], "rate": bucket["rate"]}
        return {k: {"tokens": int(b["tokens"]), "max": b["max_tokens"]} for k, b in self.buckets.items()}


def handler(request, response):
    rl = RateLimiter()
    return rl.status()


def demo():
    rl = RateLimiter(default_rate=60, default_burst=10)
    print("=== Rate Limiter ===")
    for i in range(12):
        result = rl.allow("user_1")
        status = "ALLOWED" if result["allowed"] else "BLOCKED"
        print(f"  Request {i+1}: {status} (remaining: {result['remaining']})")
    print(f"\n  Status: {rl.status('user_1')}")
    return rl.status()


if __name__ == "__main__":
    demo()
