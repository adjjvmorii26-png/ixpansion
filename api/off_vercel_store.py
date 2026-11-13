"""Off-Vercel state store.

Vercel serverless filesystems are ephemeral. Prefer an external durable store.
GitHub is cold-archive only; /tmp is an explicitly ephemeral fallback.

Environment:
  UPSTASH_REDIS_REST_URL + UPSTASH_REDIS_REST_TOKEN
  IXP_STATE_HTTP_GET + IXP_STATE_HTTP_PUT
  IXP_GITHUB_TOKEN (cold reads only)

Configured backend failures raise StoreError. They never silently fall back to
/tmp or return a caller's default, which could disguise data loss.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class StoreError(RuntimeError):
    """A configured persistence backend could not complete an operation."""


class StoreConfigurationError(StoreError):
    """Persistence environment variables are incomplete or invalid."""


def _key(key: str) -> str:
    if not isinstance(key, str) or not key or key in {".", ".."}:
        raise ValueError("storage key must be a non-empty string")
    if any(ord(char) < 32 or ord(char) == 127 for char in key):
        raise ValueError("storage key must not contain control characters")
    return key


def _encoded_key(key: str) -> str:
    return urllib.parse.quote(_key(key), safe="")


def _upstash_url() -> str:
    return (os.environ.get("UPSTASH_REDIS_REST_URL") or "").rstrip("/")


def _upstash_token() -> str:
    return os.environ.get("UPSTASH_REDIS_REST_TOKEN") or ""


def backend() -> str:
    redis_url = _upstash_url()
    redis_token = _upstash_token()
    if bool(redis_url) != bool(redis_token):
        raise StoreConfigurationError(
            "UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN must be set together"
        )
    if redis_url:
        parsed = urllib.parse.urlparse(redis_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise StoreConfigurationError("Upstash REST URL must be a valid HTTPS URL")
        return "upstash"

    http_get = os.environ.get("IXP_STATE_HTTP_GET")
    http_put = os.environ.get("IXP_STATE_HTTP_PUT")
    if bool(http_get) != bool(http_put):
        raise StoreConfigurationError(
            "IXP_STATE_HTTP_GET and IXP_STATE_HTTP_PUT must be set together"
        )
    if http_get:
        return "http"
    if os.environ.get("IXP_GITHUB_TOKEN"):
        return "github_cold"
    return "tmp_only"


def _read_response(response: Any) -> Any:
    try:
        body = json.loads(response.read().decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StoreError("storage backend returned invalid JSON") from exc
    if isinstance(body, dict) and body.get("error"):
        raise StoreError(f"storage backend error: {body['error']}")
    if isinstance(body, dict) and "result" in body:
        return body["result"]
    return body


def _open(request: urllib.request.Request) -> Any:
    try:
        return urllib.request.urlopen(request, timeout=8)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise StoreError(f"storage backend request failed: {exc}") from exc


def _decode_value(result: Any, default: Any) -> Any:
    if result is None:
        return default
    if isinstance(result, str):
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return result
    return result


def _cache_read(key: str):
    try:
        from api.squirrel_cache import SquirrelCache
        return SquirrelCache().get(key)
    except Exception:
        # Cache is an optimization; failures must not mask the source store.
        return False, None


def _cache_write(key: str, value: Any, ttl: float) -> None:
    if ttl <= 0:
        return
    try:
        from api.squirrel_cache import SquirrelCache
        SquirrelCache().put(key, value, ttl=ttl)
    except Exception:
        # The durable write already succeeded; cache failure is non-fatal.
        return


def get_json(key: str, default: Any = None, cache_ttl: float = 0) -> Any:
    key = _key(key)
    b = backend()
    if cache_ttl > 0 and b in {"upstash", "http"}:
        hit, cached = _cache_read(key)
        if hit:
            return cached
    if b == "upstash":
        url = f"{_upstash_url()}/get/{_encoded_key(key)}"
        req = urllib.request.Request(
            url, headers={"Authorization": f"Bearer {_upstash_token()}"}
        )
        with _open(req) as response:
            value = _decode_value(_read_response(response), default)
        if value is not default:
            _cache_write(key, value, cache_ttl)
        return value

    if b == "http":
        url = os.environ["IXP_STATE_HTTP_GET"].format(key=_encoded_key(key))
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with _open(req) as response:
            try:
                value = json.loads(response.read().decode("utf-8") or "null")
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise StoreError("HTTP storage backend returned invalid JSON") from exc
        if value is not None:
            _cache_write(key, value, cache_ttl)
        return value

    if b == "github_cold":
        try:
            from api.github_mirror import gh_read
            value = gh_read(f"data/{_encoded_key(key)}.json")
        except Exception as exc:
            raise StoreError(f"GitHub cold-archive read failed: {exc}") from exc
        return default if value is None else value

    # Explicitly ephemeral fallback. Never treat this as durable storage.
    path = f"/tmp/ixp_state_{hashlib.sha256(key.encode()).hexdigest()}.json"
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return default
    except (OSError, json.JSONDecodeError) as exc:
        raise StoreError(f"temporary state read failed: {exc}") from exc


def set_json(key: str, value: Any, cache_ttl: float = 0) -> bool:
    key = _key(key)
    payload = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    b = backend()

    if b == "upstash":
        url = f"{_upstash_url()}/set/{_encoded_key(key)}"
        req = urllib.request.Request(
            url,
            data=payload.encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {_upstash_token()}",
                "Content-Type": "application/json",
            },
        )
        with _open(req) as response:
            result = _read_response(response)
        if result != "OK":
            raise StoreError(f"Upstash SET returned unexpected result: {result!r}")
        _cache_write(key, value, cache_ttl)
        return True

    if b == "http":
        url = os.environ["IXP_STATE_HTTP_PUT"].format(key=_encoded_key(key))
        req = urllib.request.Request(
            url,
            data=payload.encode("utf-8"),
            method="PUT",
            headers={"Content-Type": "application/json"},
        )
        with _open(req) as response:
            _read_response(response)
        _cache_write(key, value, cache_ttl)
        return True

    if b == "github_cold":
        # Archive writes remain disabled unless explicitly enabled.
        if os.environ.get("IXP_ALLOW_GITHUB_HOT_WRITE", "").lower() not in {
            "1", "true", "yes"
        }:
            return False
        try:
            from api.github_mirror import gh_write
            return bool(gh_write(
                f"data/{_encoded_key(key)}.json",
                value if isinstance(value, dict) else {"value": value},
                f"cold store {key}",
            ))
        except Exception as exc:
            raise StoreError(f"GitHub archive write failed: {exc}") from exc

    path = f"/tmp/ixp_state_{hashlib.sha256(key.encode()).hexdigest()}.json"
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(payload)
    except OSError as exc:
        raise StoreError(f"temporary state write failed: {exc}") from exc
    return True


def coherence_vitals():
    try:
        selected = backend()
        return {
            "module": "off_vercel_store",
            "backend": selected,
            "durable": selected in {"upstash", "http"},
            "ok": True,
        }
    except StoreConfigurationError as exc:
        return {
            "module": "off_vercel_store",
            "backend": "misconfigured",
            "durable": False,
            "ok": False,
            "error": str(exc),
        }
