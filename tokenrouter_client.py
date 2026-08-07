import json
import os
from typing import Any, Dict, Optional
from urllib import error, request


class TokenRouterClientError(RuntimeError):
    """Raised when a TokenRouter request cannot be completed."""


class TokenRouterClient:
    """Small client for TokenRouter's OpenAI-compatible chat endpoint."""

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.api_key = api_key
        self.model = model or os.getenv(
            "TOKENROUTER_MODEL", "moonshotai/kimi-k3-free"
        )
        self.endpoint = endpoint or os.getenv(
            "TOKENROUTER_API_URL", "https://api.tokenrouter.com/v1/chat/completions"
        )
        self.timeout = timeout

    def complete(self, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an intelligent assistant, please reply concisely.",
                    },
                    {"role": "user", "content": prompt},
                ],
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
            raise TokenRouterClientError(
                f"TokenRouter request failed with HTTP {exc.code}: {detail}"
            ) from exc
        except (error.URLError, TimeoutError) as exc:
            raise TokenRouterClientError(
                f"TokenRouter request could not connect: {exc}"
            ) from exc
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise TokenRouterClientError(
                "TokenRouter returned an invalid JSON response"
            ) from exc

        try:
            return str(body["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise TokenRouterClientError(
                "TokenRouter response did not contain message content"
            ) from exc