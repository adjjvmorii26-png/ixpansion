"""Guarded Cloudflare Browser Run Chromium session lifecycle."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable

from .routing import build_chromium_guardrails


_SESSION_ID = re.compile(r"^[A-Za-z0-9-]{8,128}$")
_API_ORIGIN = "https://api.cloudflare.com/client/v4"


class ChromiumSessionError(RuntimeError):
    """Base error for guarded Chromium session operations."""


class ChromiumSessionConfigurationError(ChromiumSessionError):
    """Required runtime configuration is missing or invalid."""


class ChromiumSessionProtocolError(ChromiumSessionError):
    """Cloudflare returned an invalid or unexpected session response."""


@dataclass(frozen=True)
class BrowserSessionLease:
    """Short-lived session handle; the websocket URL is intentionally hidden."""

    session_id: str
    websocket_url: str = field(repr=False)
    guardrails: dict[str, list[str]]
    keep_alive_ms: int


def _stdlib_transport(
    method: str,
    url: str,
    headers: dict[str, str],
    body: bytes | None,
    timeout: float,
) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ChromiumSessionProtocolError("Cloudflare response exceeds the 1 MB limit")
            if not raw:
                return response.status, {}
            try:
                parsed = json.loads(raw.decode("utf-8"))
            except (UnicodeError, ValueError):
                raise ChromiumSessionProtocolError("Cloudflare returned a non-JSON session response") from None
            return response.status, parsed if isinstance(parsed, dict) else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read(1_000_001)
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except (UnicodeError, ValueError):
            parsed = {}
        return exc.code, parsed if isinstance(parsed, dict) else {}


class CloudflareChromiumSessionLauncher:
    """Create and close Browser Run Chromium sessions with mandatory guardrails.

    The injected transport makes lifecycle tests deterministic. No session is
    created until launch() is explicitly called with runtime credentials.
    """

    def __init__(
        self,
        *,
        account_id: str,
        token: str,
        transport: Callable[..., tuple[int, dict[str, Any]]] | None = None,
        timeout: float = 10.0,
    ) -> None:
        if not isinstance(account_id, str) or not account_id.strip():
            raise ChromiumSessionConfigurationError("Cloudflare account ID is required")
        if not isinstance(token, str) or not token.strip():
            raise ChromiumSessionConfigurationError("Cloudflare Browser Run API token is required")
        self._account_id = account_id.strip()
        self._token = token.strip()
        self._transport = transport or _stdlib_transport
        self.timeout = max(1.0, min(float(timeout), 30.0))

    def _endpoint(self, suffix: str = "") -> str:
        account = urllib.parse.quote(self._account_id, safe="")
        return f"{_API_ORIGIN}/accounts/{account}/browser-run/devtools/browser{suffix}"

    def _request(self, method: str, url: str, payload: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }
        body = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        try:
            return self._transport(method, url, headers, body, self.timeout)
        except ChromiumSessionError:
            raise
        except Exception as exc:
            raise ChromiumSessionError(
                f"Browser Run transport failed: {type(exc).__name__}"
            ) from None

    def launch(
        self,
        *,
        allowed_hosts: set[str] | None = None,
        allowed_domain_sets: set[str] | None = None,
        allow_no_network: bool = False,
        keep_alive_ms: int = 60_000,
    ) -> BrowserSessionLease:
        """Acquire a Chromium session with a mandatory, bounded guardrail policy."""
        if (
            isinstance(keep_alive_ms, bool)
            or not isinstance(keep_alive_ms, int)
            or not 10_000 <= keep_alive_ms <= 1_200_000
        ):
            raise ChromiumSessionConfigurationError(
                "keep_alive_ms must be an integer between 10000 and 1200000"
            )
        try:
            guardrails = build_chromium_guardrails(
                allowed_hosts=allowed_hosts,
                allowed_domain_sets=allowed_domain_sets,
                allow_no_network=allow_no_network,
            )
        except (TypeError, ValueError) as exc:
            raise ChromiumSessionConfigurationError(str(exc)) from None

        url = self._endpoint() + "?keep_alive=" + str(keep_alive_ms)
        status, response = self._request("POST", url, {"guardrails": guardrails})
        if status == 429 or status >= 500:
            raise ChromiumSessionError(f"Browser Run transient HTTP {status}")
        if status < 200 or status >= 300:
            raise ChromiumSessionError(f"Browser Run rejected session request with HTTP {status}")
        session_id = response.get("sessionId")
        websocket_url = response.get("webSocketDebuggerUrl")
        if (
            not isinstance(session_id, str)
            or not _SESSION_ID.fullmatch(session_id)
            or not isinstance(websocket_url, str)
        ):
            raise ChromiumSessionProtocolError("Browser Run response omitted a valid sessionId or websocket URL")

        expected_path = urllib.parse.urlsplit(self._endpoint("/" + session_id)).path
        try:
            parsed_ws = urllib.parse.urlsplit(websocket_url)
        except ValueError:
            raise ChromiumSessionProtocolError("Browser Run returned a malformed websocket URL") from None
        if not (
            parsed_ws.scheme == "wss"
            and parsed_ws.hostname == "api.cloudflare.com"
            and parsed_ws.port in (None, 443)
            and parsed_ws.path == expected_path
            and not parsed_ws.username
            and not parsed_ws.password
            and not parsed_ws.fragment
            and not parsed_ws.query
        ):
            raise ChromiumSessionProtocolError("Browser Run returned an unexpected websocket endpoint")

        return BrowserSessionLease(
            session_id=session_id,
            websocket_url=websocket_url,
            guardrails=guardrails,
            keep_alive_ms=keep_alive_ms,
        )

    def close(self, lease: BrowserSessionLease) -> None:
        """Close only a validated session lease returned by this launcher."""
        if not isinstance(lease, BrowserSessionLease) or not _SESSION_ID.fullmatch(lease.session_id):
            raise ChromiumSessionConfigurationError("a valid BrowserSessionLease is required")
        status, _ = self._request("DELETE", self._endpoint("/" + lease.session_id), None)
        if status not in (200, 202, 204):
            raise ChromiumSessionError(f"Browser Run rejected session close with HTTP {status}")
