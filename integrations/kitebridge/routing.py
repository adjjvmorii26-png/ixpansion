"""Deterministic route policy for federated browser tasks."""
from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class BrowserTask:
    url: str
    public: bool = True
    authenticated: bool = False
    persistent_session: bool = False
    requires_webgl: bool = False
    requires_video: bool = False
    bot_challenge: bool = False


def _normalize_dns_host(value: str) -> str:
    host = value.encode("idna").decode("ascii").lower().rstrip(".")
    if not host or "." not in host:
        raise ValueError("an exact fully-qualified hostname is required")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return host
    raise ValueError("IP-literal hosts are not allowed")


def select_browser_route(task: BrowserTask, *, allowed_hosts: set[str]) -> str:
    """Return kitesurf, chromium, or deny; never infer auth from URL alone."""
    if not task.public:
        return "deny"
    if (
        task.authenticated
        or task.persistent_session
        or task.requires_webgl
        or task.requires_video
        or task.bot_challenge
    ):
        return "chromium"
    if not isinstance(task.url, str) or len(task.url) > 2048:
        return "deny"
    try:
        parsed = urlsplit(task.url)
        hostname = _normalize_dns_host(parsed.hostname or "")
        port = parsed.port
        normalized_allowlist = {_normalize_dns_host(host) for host in allowed_hosts}
    except (ValueError, UnicodeError, AttributeError):
        return "deny"
    if (
        parsed.scheme.lower() == "https"
        and not parsed.username
        and not parsed.password
        and port in (None, 443)
        and not parsed.fragment
        and hostname in normalized_allowlist
    ):
        return "kitesurf"
    return "deny"
