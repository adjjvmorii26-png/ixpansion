"""CORS Middleware — Cross-Origin Resource Sharing headers.

Adds CORS headers to all API responses. Supports configurable
origins, methods, and headers.
"""
from __future__ import annotations

import json
import time
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEFAULT_ORIGINS = ["*"]
DEFAULT_METHODS = ["GET", "POST", "OPTIONS"]
DEFAULT_HEADERS = ["Content-Type", "Authorization", "X-Request-ID"]
MAX_AGE = 86400


class CORSMiddleware:
    def __init__(self, origins=None, methods=None, headers=None):
        self.origins = origins or DEFAULT_ORIGINS
        self.methods = methods or DEFAULT_METHODS
        self.headers = headers or DEFAULT_HEADERS
        self.request_count = 0

    def preflight(self, origin: str = "*") -> Dict[str, str]:
        self.request_count += 1
        return {
            "Access-Control-Allow-Origin": origin if origin in self.origins or "*" in self.origins else "",
            "Access-Control-Allow-Methods": ", ".join(self.methods),
            "Access-Control-Allow-Headers": ", ".join(self.headers),
            "Access-Control-Max-Age": str(MAX_AGE),
            "Access-Control-Allow-Credentials": "true",
        }

    def apply(self, origin: str = "*") -> Dict[str, str]:
        self.request_count += 1
        allowed = origin if (origin in self.origins or "*" in self.origins) else ""
        return {
            "Access-Control-Allow-Origin": allowed,
            "Access-Control-Allow-Methods": ", ".join(self.methods),
            "Access-Control-Allow-Headers": ", ".join(self.headers),
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Expose-Headers": "X-Request-ID, X-Rate-Limit",
        }

    def stats(self) -> Dict:
        return {
            "origins": self.origins,
            "methods": self.methods,
            "headers": self.headers,
            "request_count": self.request_count,
        }


_middleware = CORSMiddleware()


def handler(request, response):
    return _middleware.stats()


def demo():
    m = CORSMiddleware()
    print("=== CORS Middleware ===")
    headers = m.apply("https://example.com")
    print(f"\nHeaders for origin:")
    for k, v in headers.items():
        print(f"  {k}: {v}")
    print(f"\nRequests handled: {m.request_count}")
    return m.stats()


if __name__ == "__main__":
    demo()
