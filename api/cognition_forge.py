"""Wave 142 — Cognition Forge.

Tempers each agent's mind into a specialized thinker: strategist,
reasoner, poet, or paradox-tamer. When the frontier is silent, the
forge forges with cold logic instead. This is the intelligence
workbench of the workforce — no agent thinks alike twice.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

try:
    import gateway_ink
except Exception:  # pragma: no cover
    gateway_ink = None

SPECIALIZATIONS: Dict[str, str] = {
    "strategist": "Think step-by-step like a grand strategist. Give a crisp action plan.",
    "reasoner": "Reason carefully and lay out the inference chain before the conclusion.",
    "poet": "Answer with vivid, elegant, evocative language; distill the essence poetically.",
    "paradox": "Embrace contradiction; hold two opposing truths and synthesize them.",
}

DEFAULT_SPEC = "reasoner"


def _relay(role: str, prompt: str, model: str, max_tokens: int = 220,
           reasoning_effort: Optional[str] = None) -> Dict[str, Any]:
    system = SPECIALIZATIONS.get(role, SPECIALIZATIONS[DEFAULT_SPEC])
    fallback = f"cold-logic {role} reasoning on: {prompt[:80]}"
    if gateway_ink is not None:
        return gateway_ink.relay(prompt, model=model, system=system, max_tokens=max_tokens,
                                 fallback=fallback, reasoning_effort=reasoning_effort)
    return {"ok": False, "reply": fallback,
            "model": model, "reason": "gateway_ink unavailable"}


def cognition_forge_handler(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action") or "status"
    role = payload.get("role") or DEFAULT_SPEC
    prompt = str(payload.get("prompt") or "")
    model = payload.get("model")

    if action == "status":
        return {"status": "active", "forge": "Cognition Forge",
                "specializations": list(SPECIALIZATIONS),
                "default": DEFAULT_SPEC}

    if action == "roles":
        return {"status": "active", "roles": [
            {"key": k, "instruction": v} for k, v in SPECIALIZATIONS.items()]}

    if action == "think":
        if not prompt:
            return {"status": "active", "error": "provide a 'prompt'", "action": action}
        t0 = time.time()
        result = _relay(role, prompt, model,
                        max_tokens=int(payload.get("max_tokens", 220)),
                        reasoning_effort=payload.get("reasoning_effort"))
        return {"status": "active", "role": role, "prompt": prompt,
                "served": result.get("ok"), "reason": result.get("reason"),
                "cognition": result.get("reply"), "model": result.get("model"),
                "latency_ms": result.get("latency_ms"), "elapsed_ms_ms": round((time.time() - t0) * 1000, 1)}

    return {"status": "active", "error": f"unknown action '{action}'",
            "available": ["status", "roles", "think"]}


SPECIALIZATIONS_EXTRA: List[str] = []  # keep import surface stable
