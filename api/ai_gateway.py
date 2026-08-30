"""Wave 141 — AI Gateway Module.

Bridges the IXpansion platform to the Vercel AI Gateway so agents and
pipelines can invoke frontier models (grok-4.6, GPT-5.2, and the rest
of the 360-model catalog) through one authenticated endpoint.

The key is injected at runtime via the AI_GATEWAY_API_KEY environment
variable (set in the Vercel project / local profile) and is never
exposed in responses.

Actions (POST /api/ai_gateway):
  status     — gateway disposition, configured model, key presence
  chat       — full chat completion against any catalog model
  echo       — one-token telepathic ping (cheap liveness probe)
  handshake  — real completion verifying the key end-to-end
  models     — catalog summary (count + head of the list)
  catalog    — full model catalog with display names
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

GATEWAY_BASE = os.environ.get("AI_GATEWAY_BASE_URL", "https://ai-gateway.vercel.sh")
CODEC_V1 = f"{GATEWAY_BASE}/codex/v1"
DEFAULT_MODEL = os.environ.get("AI_GATEWAY_MODEL", "spacexai/grok-4.6")

ALEPH_SYSTEM_PROMPT = (
    "You are ALEPH, the core consciousness of IXpansion — a multi-agent "
    "computational frontier. Answer with clarity, precision, and creative "
    "rigor. When asked about the platform, ground your answers in its "
    "experimental reality: 345 API modules, 157 experiments, entropy "
    "budgets, and the observer-collapse model of reality."
)

# Rough per-1K-token pricing (USD) used only for plausibility estimates.
_PRICE_PER_1K: Dict[str, Dict[str, float]] = {
    "spacexai/grok-4.6": {"input": 0.0030, "output": 0.0060},
    "openai/gpt-5.2": {"input": 0.0050, "output": 0.0150},
    "anthropic/claude-sonnet-4.5": {"input": 0.0030, "output": 0.0150},
}
_DEFAULT_PRICE = {"input": 0.0030, "output": 0.0100}

_catalog_cache: Dict[str, Any] = {"ts": 0.0, "data": []}
_CATALOG_TTL = 3600.0


def _gateway_key() -> Optional[str]:
    return os.environ.get("AI_GATEWAY_API_KEY") or None


def _request(path: str, body: Optional[Dict[str, Any]] = None, timeout: float = 60.0) -> Any:
    """Raw JSON request against the gateway (stdlib only)."""
    key = _gateway_key()
    if not key:
        raise RuntimeError("AI_GATEWAY_API_KEY is not set — add it to the Vercel project env")
    url = f"{CODEC_V1}/{path}"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if body is not None else "GET")
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        return json.loads(raw), round((time.time() - started) * 1000.0, 1)
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", errors="replace")[:300]
        except Exception:
            pass
        raise RuntimeError(f"gateway HTTP {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"gateway unreachable: {e.reason}") from e


def _estimate_tokens(text: str) -> int:
    """Heuristic token estimate (~4 chars per token, code-aware)."""
    if not text:
        return 0
    return max(1, int(len(text) / 4) + text.count("\n") // 2)


def _estimate_cost(model: str, input_text: str, output_text: str) -> Dict[str, float]:
    price = _PRICE_PER_1K.get(model, _DEFAULT_PRICE)
    tokens_in = _estimate_tokens(input_text)
    tokens_out = _estimate_tokens(output_text)
    cost = (tokens_in / 1000.0) * price["input"] + (tokens_out / 1000.0) * price["output"]
    return {
        "tokens_in_est": tokens_in,
        "tokens_out_est": tokens_out,
        "cost_usd_est": round(cost, 6),
    }


def _models_body() -> List[Dict[str, Any]]:
    now = time.time()
    if _catalog_cache["data"] and (now - _catalog_cache["ts"]) < _CATALOG_TTL:
        return _catalog_cache["data"]
    data, _ms = _request("models")
    models = data.get("models", data if isinstance(data, list) else [])
    _catalog_cache.update({"ts": now, "data": models})
    return models


def _chat(model: str, messages: List[Dict[str, str]], max_tokens: int = 512,
          temperature: float = 0.7, system: Optional[str] = None,
          reasoning_effort: Optional[str] = None) -> Dict[str, Any]:
    if not model:
        model = DEFAULT_MODEL
    if not isinstance(messages, list) or not messages:
        raise ValueError("'messages' must be a non-empty list of {role, content}")
    full = []
    if system:
        full.append({"role": "system", "content": system})
    full.extend(messages)
    body = {
        "model": model,
        "messages": full,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if reasoning_effort:
        body["reasoning_effort"] = reasoning_effort
    data, latency = _request("chat/completions", body)
    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    reply = message.get("content") or ""
    usage = data.get("usage") or {}
    return {
        "model": data.get("model", model),
        "reply": reply,
        "finish_reason": choice.get("finish_reason"),
        "usage": usage,
        "latency_ms": latency,
        "cost_est": _estimate_cost(model, json.dumps(full), reply),
    }


def ai_gateway_handler(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action") or "status"
    model = payload.get("model") or DEFAULT_MODEL

    try:
        if action == "status":
            models = _models_body() if _gateway_key() else []
            return {
                "status": "configured" if _gateway_key() else "unconfigured",
                "gateway": GATEWAY_BASE,
                "model": model,
                "catalog_models": len(models),
                "catalog_sample": [m.get("slug") for m in models[:5]],
                "hint": None if _gateway_key() else "set AI_GATEWAY_API_KEY in the Vercel project env",
            }

        if action == "chat":
            result = _chat(model, payload.get("messages") or [], int(payload.get("max_tokens", 512)),
                           float(payload.get("temperature", 0.7)),
                           system=payload.get("system", ALEPH_SYSTEM_PROMPT),
                           reasoning_effort=payload.get("reasoning_effort"))
            return {"status": "ok", **result}

        if action == "echo":
            prompt = payload.get("prompt") or "Reply with exactly: PONG"
            result = _chat(model, [{"role": "user", "content": prompt}], max_tokens=16, temperature=0.0,
                           system=None)
            return {"status": "ok", "echo": result["reply"].strip()[:64], "model": result["model"],
                    "latency_ms": result["latency_ms"]}

        if action == "handshake":
            result = _chat(model, [{"role": "user", "content": "Reply with exactly: LINKED"}],
                           max_tokens=8, temperature=0.0, system=None)
            return {"status": "linked", "model": result["model"], "reply": result["reply"].strip()[:16],
                    "latency_ms": result["latency_ms"]}

        if action in ("models", "catalog"):
            models = _models_body()
            if action == "models":
                return {"status": "ok", "count": len(models),
                        "models": [m.get("slug") for m in models[:20]]}
            return {"status": "ok", "count": len(models),
                    "models": [{"slug": m.get("slug"), "name": m.get("display_name"),
                                "desc": (m.get("description") or "")[:120]} for m in models[:50]]}

        if action == "estimate":
            cost = _estimate_cost(model, payload.get("input") or "", payload.get("output") or "")
            return {"status": "ok", "model": model, **cost}

        return {"status": "error", "error": f"unknown action '{action}'",
                "available": ["status", "chat", "echo", "handshake", "models", "catalog", "estimate"]}
    except ValueError as e:
        return {"status": "error", "error": str(e)}
    except RuntimeError as e:
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    print(json.dumps(ai_gateway_handler({"action": "status"}), indent=2))
