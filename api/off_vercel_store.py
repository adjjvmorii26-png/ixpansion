"""Off-Vercel state store.

Vercel serverless FS is ephemeral. Vercel Blob/KV still counts as Vercel storage.
This module prefers external stores, then cold GitHub archive, then /tmp only.

Env (set one):
  UPSTASH_REDIS_REST_URL + UPSTASH_REDIS_REST_TOKEN  — recommended
  TURSO_DATABASE_URL + TURSO_AUTH_TOKEN               — optional SQL
  IXP_STATE_HTTP_GET / IXP_STATE_HTTP_PUT            — generic HTTPS JSON API
  IXP_GITHUB_TOKEN                                    — cold archive only (not hot path)

Never write hot counters/logs into the git tree from production.
"""
from __future__ import annotations
import json, os, urllib.request
from typing import Any, Optional
from urllib.error import HTTPError


def _upstash_url() -> str:
    return (os.environ.get("UPSTASH_REDIS_REST_URL") or "").rstrip("/")


def _upstash_token() -> str:
    return os.environ.get("UPSTASH_REDIS_REST_TOKEN") or ""


def backend() -> str:
    if _upstash_url() and _upstash_token():
        return "upstash"
    if os.environ.get("IXP_STATE_HTTP_GET") and os.environ.get("IXP_STATE_HTTP_PUT"):
        return "http"
    if os.environ.get("IXP_GITHUB_TOKEN"):
        return "github_cold"
    return "tmp_only"


def get_json(key: str, default: Any = None) -> Any:
    b = backend()
    if b == "upstash":
        try:
            url = f"{_upstash_url()}/get/{key}"
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {_upstash_token()}"},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                body = json.loads(resp.read().decode() or "{}")
            result = body.get("result")
            if result is None:
                return default
            if isinstance(result, str):
                try:
                    return json.loads(result)
                except Exception:
                    return result
            return result
        except Exception:
            return default
    if b == "http":
        try:
            url = os.environ["IXP_STATE_HTTP_GET"].format(key=key)
            with urllib.request.urlopen(url, timeout=8) as resp:
                return json.loads(resp.read().decode() or "null")
        except Exception:
            return default
    if b == "github_cold":
        try:
            from api.github_mirror import gh_read
            return gh_read(f"data/{key}.json") or default
        except Exception:
            return default
    # tmp_only
    path = f"/tmp/ixp_state_{key}.json"
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def set_json(key: str, value: Any) -> bool:
    payload = json.dumps(value)
    b = backend()
    if b == "upstash":
        try:
            # REST: POST /set/{key} with body as value
            url = f"{_upstash_url()}/set/{key}"
            req = urllib.request.Request(
                url,
                data=payload.encode(),
                method="POST",
                headers={
                    "Authorization": f"Bearer {_upstash_token()}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                resp.read()
            return True
        except Exception:
            return False
    if b == "http":
        try:
            url = os.environ["IXP_STATE_HTTP_PUT"].format(key=key)
            req = urllib.request.Request(
                url,
                data=payload.encode(),
                method="PUT",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                resp.read()
            return True
        except Exception:
            return False
    if b == "github_cold":
        # Explicit: only for rare archival writes, not every request
        if os.environ.get("IXP_ALLOW_GITHUB_HOT_WRITE", "").lower() not in {"1", "true", "yes"}:
            return False
        try:
            from api.github_mirror import gh_write
            return gh_write(f"data/{key}.json", value if isinstance(value, dict) else {"value": value}, f"cold store {key}")
        except Exception:
            return False
    path = f"/tmp/ixp_state_{key}.json"
    try:
        with open(path, "w") as f:
            f.write(payload)
        return True
    except Exception:
        return False


def coherence_vitals():
    return {"module": "off_vercel_store", "backend": backend(), "ok": True}
