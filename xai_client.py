import json
import os
from typing import Any, Dict, Optional
from urllib import error, request


class XAIClientError(RuntimeError):
    """Raised when an xAI request cannot be completed."""


class XAIClient:
    """Small client for xAI's OpenAI-compatible chat completions endpoint."""

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.api_key = api_key
        self.model = model or os.getenv("XAI_MODEL", "grok-3-mini")
        self.endpoint = endpoint or os.getenv(
            "XAI_API_URL", "https://api.x.ai/v1/chat/completions"
        )
        self.timeout = timeout

    def complete(self, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode("utf-8")
        http_request = request.Request(
            self.endpoint,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=self.timeout) as response:
                body: Dict[str, Any] = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise XAIClientError(
                f"xAI request failed with HTTP {exc.code}: {detail}"
            ) from exc
        except (error.URLError, TimeoutError) as exc:
            raise XAIClientError(f"xAI request could not connect: {exc}") from exc
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise XAIClientError("xAI returned an invalid JSON response") from exc

        try:
            return str(body["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise XAIClientError(
                "xAI response did not contain message content"
            ) from exc