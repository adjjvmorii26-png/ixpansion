"""Deterministic route policy and Cloudflare guardrails for browser tasks."""
from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlsplit


_DNS_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


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
    labels = host.split(".")
    if (
        not host
        or len(host) > 253
        or len(labels) < 2
        or any(not _DNS_LABEL.fullmatch(label) for label in labels)
    ):
        raise ValueError("an exact fully-qualified DNS hostname is required")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return host
    raise ValueError("IP-literal hosts are not allowed")


def build_chromium_guardrails(*, allowed_hosts: set[str]) -> dict[str, list[str]]:
    """Build Cloudflare Browser Run guardrails for a Chromium session.

    Cloudflare documents allowedDomains for Puppeteer/Playwright sessions;
    these guardrails are not supported by Kitesurf.
    """
    normalized = sorted({_normalize_dns_host(host) for host in allowed_hosts})
    if not normalized:
        raise ValueError("at least one exact allowed hostname is required")
    return {"allowedDomains": normalized}


def select_browser_route(task: BrowserTask, *, allowed_hosts: set[str]) -> str:
    """Return kitesurf, chromium, or deny after applying one target policy.

    The exact-host allowlist and URL safety checks apply to every engine.
    Engine capability flags may select Chromium, but never bypass target policy.
    """
    if not task.public or not isinstance(task.url, str) or len(task.url) > 2048:
        return "deny"
    try:
        parsed = urlsplit(task.url)
        hostname = _normalize_dns_host(parsed.hostname or "")
        port = parsed.port
        normalized_allowlist = {_normalize_dns_host(host) for host in allowed_hosts}
    except (ValueError, UnicodeError, AttributeError):
        return "deny"
    if not (
        parsed.scheme.lower() == "https"
        and not parsed.username
        and not parsed.password
        and port in (None, 443)
        and not parsed.fragment
        and hostname in normalized_allowlist
    ):
        return "deny"
    if (
        task.authenticated
        or task.persistent_session
        or task.requires_webgl
        or task.requires_video
        or task.bot_challenge
    ):
        return "chromium"
    return "kitesurf"
