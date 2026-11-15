"""Deterministic route policy for federated browser tasks."""
from __future__ import annotations

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
    try:
        parsed = urlsplit(task.url)
        hostname = (parsed.hostname or "").encode("idna").decode("ascii").lower().rstrip(".")
    except (ValueError, UnicodeError):
        return "deny"
    normalized_allowlist = {
        host.encode("idna").decode("ascii").lower().rstrip(".")
        for host in allowed_hosts
    }
    if parsed.scheme.lower() == "https" and hostname in normalized_allowlist:
        return "kitesurf"
    return "deny"
