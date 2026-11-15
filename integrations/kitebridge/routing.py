"""Deterministic route policy and Cloudflare Browser Run guardrails."""
from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlsplit


_DNS_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
_DOMAIN_SET = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


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
        raise ValueError("a fully-qualified DNS hostname is required")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return host
    raise ValueError("IP-literal hosts are not allowed")


def _normalize_domain_pattern(value: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError("domain patterns must be non-empty hostnames")
    if value.startswith("*."):
        return "*." + _normalize_dns_host(value[2:])
    if "*" in value:
        raise ValueError("only a single leading wildcard is supported")
    return _normalize_dns_host(value)


def build_chromium_guardrails(
    *,
    allowed_hosts: set[str] | None = None,
    allowed_domain_sets: set[str] | None = None,
    allow_no_network: bool = False,
) -> dict[str, list[str]]:
    """Compile a fail-closed Cloudflare Browser Run session guardrail object.

    Cloudflare applies session guardrails to HTTP/HTTPS requests in
    Puppeteer, Playwright, and CDP sessions. They are not available to
    Browser Run Quick Actions such as Kitesurf snapshots.
    """
    hosts = allowed_hosts or set()
    domain_sets = allowed_domain_sets or set()
    if not isinstance(hosts, set) or not isinstance(domain_sets, set):
        raise ValueError("allowed_hosts and allowed_domain_sets must be sets")
    if len(hosts) > 50:
        raise ValueError("Cloudflare Browser Run allows at most 50 allowedDomains entries")
    if len(domain_sets) > 4:
        raise ValueError("Cloudflare Browser Run allows at most four allowedDomainSets entries")

    normalized_hosts = sorted({_normalize_domain_pattern(host) for host in hosts})
    normalized_sets = sorted(domain_sets)
    if any(
        not isinstance(name, str)
        or not _DOMAIN_SET.fullmatch(name)
        for name in normalized_sets
    ):
        raise ValueError("domain-set names must be non-empty identifiers without whitespace")
    if not normalized_hosts and not normalized_sets and not allow_no_network:
        raise ValueError("an allowlist is required; use allow_no_network=True to block all web requests")
    if allow_no_network and (normalized_hosts or normalized_sets):
        raise ValueError("allow_no_network cannot be combined with allowed domains or domain sets")

    guardrails: dict[str, list[str]] = {"allowedDomains": normalized_hosts}
    if normalized_sets:
        guardrails["allowedDomainSets"] = normalized_sets
    return guardrails


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
