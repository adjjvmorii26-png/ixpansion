"""Optional, stdlib-only bridge to an OpenAI-compatible chat endpoint.

The sandbox organism is fully self-sufficient offline: idea_lab and
self_debugger both work with zero network access. When ``OPENAI_API_KEY`` and
``OPENAI_BASE_URL`` are present in the environment (as injected by the
GenSpark sandbox), this bridge lets the organism occasionally reach for a
sharper idea or a smarter repair. It fails closed: any error becomes ``None``
so callers always have an offline fallback path.
"""

from __future__ import annotations

import json
import os
from typing import List, Optional
from urllib import error, request

DEFAULT_MODEL = "gpt-5-mini"


class LLMBridgeError(RuntimeError):
    """Raised only for programmer errors; runtime failures return None instead."""


class LLMBridge:
    """Minimal chat-completion client. Never required for the organism to run."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "")).rstrip("/")
        self.model = model or os.getenv("SANDBOX_LLM_MODEL", DEFAULT_MODEL)
        self.timeout = timeout

    @property
    def available(self) -> bool:
        return bool(self.api_key and self.base_url)

    def chat(self, system: str, user: str) -> Optional[str]:
        """Return a completion, or None if the bridge is unavailable or fails."""
        if not self.available:
            return None
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            }
        ).encode("utf-8")
        http_request = request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            return str(body["choices"][0]["message"]["content"])
        except (error.HTTPError, error.URLError, TimeoutError, OSError):
            return None
        except (json.JSONDecodeError, UnicodeDecodeError, KeyError, IndexError, TypeError):
            return None

    @staticmethod
    def extract_code(text: str) -> str:
        """Pull the first fenced code block out of an LLM response, if any."""
        if "```" not in text:
            return text.strip()
        parts = text.split("```")
        for chunk in parts[1::2]:
            lines = chunk.splitlines()
            if lines and lines[0].strip().lower() in {"python", "py", ""}:
                return "\n".join(lines[1:]).strip()
            return chunk.strip()
        return text.strip()
