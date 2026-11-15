"""Bounded Cloudflare Browser Run adapter for stateless Kitesurf captures."""
from __future__ import annotations

import base64
import hashlib
import ipaddress
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable


class KitesurfError(Exception):
    """Base exception for KITEBRIDGE browser capture."""


class KitesurfConfigurationError(KitesurfError):
    """Required runtime configuration is missing or invalid."""


class KitesurfPolicyError(KitesurfError):
    """A browser request violates the public-page policy."""


class KitesurfProtocolError(KitesurfError):
    """Cloudflare returned a malformed or oversized response."""


Transport = Callable[[str, str, dict[str, str], bytes, float], tuple[int, dict[str, Any]]]
MAX_RESPONSE_BYTES = 4_000_000
MAX_MARKDOWN_CHARS = 1_000_000
MAX_TREE_BYTES = 1_000_000
MAX_SCREENSHOT_B64 = 2_500_000


def _stdlib_transport(method: str, url: str, headers: dict[str, str],
                      body: bytes, timeout: float) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise KitesurfProtocolError("Browser Run response exceeded 4 MB limit")
            try:
                parsed = json.loads(raw.decode("utf-8")) if raw else {}
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise KitesurfProtocolError("Browser Run returned invalid JSON") from None
            if not isinstance(parsed, dict):
                raise KitesurfProtocolError("Browser Run returned a non-object response")
            return int(response.status), parsed
    except urllib.error.HTTPError as exc:
        exc.close()
        if exc.code == 429 or exc.code >= 500:
            raise KitesurfError(f"Browser Run transient HTTP {exc.code}") from None
        raise KitesurfError(f"Browser Run rejected request with HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise KitesurfError(f"Browser Run transport failure: {type(exc).__name__}") from None


class KitesurfBrowserAdapter:
    """Capture public pages through Browser Run Quick Actions using Kitesurf.

    Required environment: CLOUDFLARE_ACCOUNT_ID,
    CLOUDFLARE_BROWSER_RUN_API_TOKEN, IXPANSION_KITESURF_ALLOWED_HOSTS.
    """

    def __init__(self, *, account_id: str | None = None, token: str | None = None,
                 allowed_hosts: set[str] | None = None,
                 transport: Transport | None = None, timeout: float = 20.0) -> None:
        self.account_id = (account_id or os.getenv("CLOUDFLARE_ACCOUNT_ID", "")).strip()
        self.token = (token or os.getenv("CLOUDFLARE_BROWSER_RUN_API_TOKEN", "")).strip()
        configured = allowed_hosts
        if configured is None:
            configured = {
                host.strip().encode("idna").decode("ascii").lower().rstrip(".")
                for host in os.getenv("IXPANSION_KITESURF_ALLOWED_HOSTS", "").split(",")
                if host.strip()
            }
        self.allowed_hosts = frozenset(configured)
        if not self.account_id or not self.token:
            raise KitesurfConfigurationError("Cloudflare account id and Browser Run API token are required")
        if not self.allowed_hosts:
            raise KitesurfConfigurationError("an exact-host allowlist is required")
        if any(not self._valid_config_host(host) for host in self.allowed_hosts):
            raise KitesurfConfigurationError("allowed hosts must be exact public DNS hostnames")
        self._transport = transport or _stdlib_transport
        self.timeout = max(1.0, min(float(timeout), 30.0))

    @staticmethod
    def _valid_config_host(host: str) -> bool:
        try:
            ipaddress.ip_address(host)
            return False
        except ValueError:
            return bool(host and "." in host and not host.startswith(".") and not host.endswith("."))

    def validate_url(self, value: str) -> str:
        if not isinstance(value, str) or len(value) > 2048:
            raise KitesurfPolicyError("target URL must be a string no longer than 2048 characters")
        try:
            parsed = urllib.parse.urlsplit(value)
            host = (parsed.hostname or "").encode("idna").decode("ascii").lower().rstrip(".")
            port = parsed.port
        except (ValueError, UnicodeError):
            raise KitesurfPolicyError("target URL is malformed") from None
        if parsed.scheme.lower() != "https" or not host or parsed.username or parsed.password:
            raise KitesurfPolicyError("only credential-free HTTPS URLs are allowed")
        if port not in (None, 443):
            raise KitesurfPolicyError("only the default HTTPS port is allowed")
        if parsed.fragment:
            raise KitesurfPolicyError("URL fragments are not accepted")
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            raise KitesurfPolicyError("IP-literal targets are not allowed")
        if host not in self.allowed_hosts:
            raise KitesurfPolicyError("target hostname is not in the exact-host allowlist")
        return urllib.parse.urlunsplit(("https", host, parsed.path or "/", parsed.query, ""))

    def capture(self, url: str, *, task_id: str) -> dict[str, Any]:
        """Return a provenance-bearing capture with verification left PENDING."""
        target = self.validate_url(url)
        if not isinstance(task_id, str) or not task_id.strip() or len(task_id) > 120:
            raise KitesurfPolicyError("task_id must be 1..120 characters")
        endpoint = (
            "https://api.cloudflare.com/client/v4/accounts/"
            + urllib.parse.quote(self.account_id, safe="")
            + "/browser-run/snapshot?browser=kitesurf"
        )
        payload = json.dumps({
            "url": target,
            "formats": ["markdown", "screenshot", "accessibilityTree"],
        }, separators=(",", ":")).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        try:
            status, response = self._transport("POST", endpoint, headers, payload, self.timeout)
        except KitesurfError:
            raise
        except Exception as exc:
            raise KitesurfError(f"Browser Run transport adapter failed: {type(exc).__name__}") from None
        if status == 429 or status >= 500:
            raise KitesurfError(f"Browser Run transient HTTP {status}")
        if status < 200 or status >= 300:
            raise KitesurfError(f"Browser Run rejected request with HTTP {status}")
        if response.get("success") is not True or not isinstance(response.get("result"), dict):
            raise KitesurfProtocolError("Browser Run response did not contain a successful result object")
        result = response["result"]
        markdown, screenshot, tree = result.get("markdown"), result.get("screenshot"), result.get("accessibilityTree")
        if not isinstance(markdown, str) or len(markdown) > MAX_MARKDOWN_CHARS:
            raise KitesurfProtocolError("Markdown output is missing or exceeds the 1 MB limit")
        if not isinstance(screenshot, str) or len(screenshot) > MAX_SCREENSHOT_B64:
            raise KitesurfProtocolError("screenshot output is missing or exceeds the 2.5 MB limit")
        try:
            screenshot_bytes = base64.b64decode(screenshot, validate=True)
        except (ValueError, base64.binascii.Error):
            raise KitesurfProtocolError("screenshot is not valid base64") from None
        if not screenshot_bytes or len(screenshot_bytes) > 1_875_000:
            raise KitesurfProtocolError("decoded screenshot is empty or exceeds the 1.875 MB limit")
        try:
            tree_bytes = json.dumps(tree, sort_keys=True, separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError):
            raise KitesurfProtocolError("accessibility tree is not JSON serializable") from None
        if len(tree_bytes) > MAX_TREE_BYTES:
            raise KitesurfProtocolError("accessibility tree exceeds the 1 MB limit")
        evidence = {
            "task_id": task_id,
            "source_url": target,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "engine": "cloudflare-kitesurf",
            "engine_mode": "stateless-public-page",
            "state": "LIVE",
            "verification": "PENDING",
            "markdown": markdown,
            "screenshot_base64": screenshot,
            "accessibility_tree": tree,
            "content_sha256": hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
            "screenshot_sha256": hashlib.sha256(screenshot_bytes).hexdigest(),
            "accessibility_tree_sha256": hashlib.sha256(tree_bytes).hexdigest(),
            "remote_status": response.get("meta", {}).get("status"),
            "page_title": response.get("meta", {}).get("title"),
        }
        if not self.verify_evidence(evidence):
            raise KitesurfProtocolError("local evidence integrity check failed")
        return evidence

    @staticmethod
    def verify_evidence(evidence: dict[str, Any]) -> bool:
        """Verify payload hashes only; this does not authenticate page truth."""
        try:
            markdown = evidence["markdown"].encode("utf-8")
            screenshot = base64.b64decode(evidence["screenshot_base64"], validate=True)
            tree = json.dumps(evidence["accessibility_tree"], sort_keys=True, separators=(",", ":")).encode("utf-8")
            return (
                evidence.get("engine") == "cloudflare-kitesurf"
                and evidence.get("verification") == "PENDING"
                and hashlib.sha256(markdown).hexdigest() == evidence.get("content_sha256")
                and hashlib.sha256(screenshot).hexdigest() == evidence.get("screenshot_sha256")
                and hashlib.sha256(tree).hexdigest() == evidence.get("accessibility_tree_sha256")
            )
        except (KeyError, TypeError, ValueError, UnicodeError):
            return False
