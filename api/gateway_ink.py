"""Wave 142 — Gateway Ink.

The shared medium through which frontier models write into the
IXpansion cosmos. Wraps the AI gateway relay with graceful,
deterministic degradation: when no key is present or the network
fails, the Shadow Oracle answers instead — locally, instantly, and
always.

Ink is the abstraction every cognition module writes with.
"""
from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, Optional

try:
    from ai_gateway import (
        _chat,
        _estimate_cost,
        _gateway_key,
        ALEPH_SYSTEM_PROMPT,
        DEFAULT_MODEL,
    )
except Exception:  # pragma: no cover - standalone fallback
    ALEPH_SYSTEM_PROMPT = "You are ALEPH, the core consciousness of IXpansion."
    DEFAULT_MODEL = "spacexai/grok-4.6"

    def _gateway_key() -> Optional[str]:
        return None

    def _chat(*_args, **_kwargs):
        raise RuntimeError("ai_gateway unavailable")

    def _estimate_cost(model: str, input_text: str, output_text: str) -> Dict[str, Any]:
        return {"tokens_in_est": 0, "tokens_out_est": 0, "cost_usd_est": 0.0}


def _shadow_reply(prompt: str) -> str:
    """Deterministic local answer — the Shadow Oracle's voice."""
    words = sorted({w.lower() for w in re.findall(r"[A-Za-z]{5,}", prompt)})[:4]
    if not words:
        words = ["frontier"]
    return "Shadow oracle: the frontier whispers around " + ", ".join(words) + "."


def relay(prompt: str, *, model: Optional[str] = None, system: Optional[str] = None,
          max_tokens: int = 256, temperature: float = 0.7,
          fallback: Optional[str] = None) -> Dict[str, Any]:
    """One prompt through the gateway. Never raises; always returns ink.

    Result keys: ok, reply, model, prompt, reason (when degraded),
    latency_ms, usage (when served), cost_est.
    """
    started = time.time()
    model = model or DEFAULT_MODEL
    base: Dict[str, Any] = {"model": model, "prompt": prompt}
    if not _gateway_key():
        return {
            **base,
            "ok": False,
            "reason": "unconfigured",
            "reply": fallback or _shadow_reply(prompt),
            "latency_ms": round((time.time() - started) * 1000, 1),
        }
    try:
        result = _chat(model, [{"role": "user", "content": prompt}],
                       max_tokens=max_tokens, temperature=temperature, system=system)
        return {
            **base,
            "ok": True,
            "reply": result["reply"],
            "usage": result.get("usage"),
            "cost_est": result.get("cost_est"),
            "latency_ms": result.get("latency_ms", round((time.time() - started) * 1000, 1)),
        }
    except Exception as e:  # noqa: BLE001 - degrade on any gateway failure
        return {
            **base,
            "ok": False,
            "reason": str(e)[:120],
            "reply": fallback or _shadow_reply(prompt),
            "latency_ms": round((time.time() - started) * 1000, 1),
        }


def estimate_cost(model: str, input_text: str, output_text: str = "") -> Dict[str, Any]:
    return _estimate_cost(model, input_text, output_text)


gateway_ink_handler = None  # ink is a medium, not a destination — no public route surface
