"""Wave 143 — Cognition Ritual.

A single invocation that walks a question through the entire cognitive
stack and returns the whole journey. One call, five minds:

  forge      — the agent picks a persona and answers
  reflect    — the same persona plays critic and interrogates its own answer
  fractal    — the question is tunneled down to its sub-scales
  fingerprint— the agent's thinking is distilled into a signature
  meter      — the consultation is metered against the spend ledger
  hexer      — the conclusion is bound into an immutable HEX artifact

The ritual never raises: every stage is optional and every stage can
fall back to cold logic. The result is the entire thought-loop, fully
traced.
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

try:
    from api import (  # noqa: F401
        cognition_forge,
        oracle_meter,
        fractal_oracle,
        cognition_fingerprint,
        dream_hexer,
    )
except Exception:  # pragma: no cover - direct import fallback
    import sys
    from pathlib import Path
    _api = str(Path(__file__).resolve().parent)
    if _api not in sys.path:
        sys.path.insert(0, _api)
    import cognition_forge, oracle_meter, fractal_oracle, cognition_fingerprint, dream_hexer  # noqa

_STAGES = ["forge", "reflect", "fractal", "fingerprint", "meter", "hexer"]


def _stage(fn, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run one stage and mark its disposition without ever raising."""
    t0 = time.time()
    try:
        result = fn(payload)
        return {"result": result, "error": None, "elapsed_ms": round((time.time() - t0) * 1000, 1)}
    except Exception as e:  # noqa: BLE001 - a stage must never sink the ritual
        return {"result": None, "error": str(e)[:160], "elapsed_ms": round((time.time() - t0) * 1000, 1)}


def _ritual_spec(role: str) -> Dict[str, str]:
    """Critic persona derived from the chosen thinker."""
    return {
        "critic_system": (
            "You are the ruthless critic of the " + role +
            " mind. Challenge the claim above, name a hidden assumption, "
            "and state what a more rigorous answer would require. Be sharp, brief, fair."
        ),
    }


def cognition_ritual_handler(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action") or "status"
    question = str(payload.get("question") or payload.get("prompt") or "")
    role = str(payload.get("role") or "reasoner")
    model = payload.get("model") or "spacexai/grok-4.6"
    agent = str(payload.get("agent") or "agent")

    if action == "status":
        return {"status": "active", "ritual": "Cognition Ritual",
                "stages": _STAGES, "default_role": "reasoner"}

    if action not in ("perform", "run", "ritual"):
        return {"status": "active", "error": f"unknown action '{action}'",
                "available": ["status", "perform"]}

    if not question:
        return {"status": "active", "error": "provide a 'question'", "action": action}

    started = time.time()
    fast = bool(payload.get("fast", False))
    max_tokens = int(payload.get("max_tokens", 220))
    reasoning_effort = payload.get("reasoning_effort") or "low"
    stages: List[Dict[str, Any]] = []
    trace: Dict[str, Any] = {}

    # 1. forge: answer as the chosen persona
    forge = _stage(cognition_forge.cognition_forge_handler,
                   {"action": "think", "role": role, "prompt": question, "model": model,
                    "max_tokens": max_tokens, "reasoning_effort": reasoning_effort})
    answer = (forge["result"] or {}).get("cognition") or ""
    trace["answer"] = answer
    trace["think_served"] = (forge["result"] or {}).get("served", False)
    stages.append({"stage": "forge", "elapsed_ms": forge["elapsed_ms"],
                   "served": trace["think_served"], "error": forge["error"]})

    # 2. reflect: the same persona plays critic on its own answer (one live call, unless fast)
    if not fast:
        critic = _stage(cognition_forge.cognition_forge_handler,
                        {"action": "think", "role": role, "prompt":
                         f"Critique this claim: '{answer or 'N/A'}'. {_ritual_spec(role)['critic_system']}",
                         "model": model, "max_tokens": max_tokens,
                         "reasoning_effort": reasoning_effort})
        critique = (critic["result"] or {}).get("cognition") or ""
        stages.append({"stage": "reflect", "elapsed_ms": critic["elapsed_ms"],
                       "served": (critic["result"] or {}).get("served", False), "error": critic["error"]})
    else:
        critique = f"(fast mode) self-critique deferred; claim: {answer[:120] or 'N/A'}"
        stages.append({"stage": "reflect", "elapsed_ms": 0, "served": False,
                       "error": None, "deferred": True})
    trace["critique"] = critique

    # 3. fractal: tunnel the question to sub-scales
    fractal = fractal_oracle.fractal_oracle_handler(
        {"action": "ask", "question": question, "model": model})
    trace["sub_answers"] = [s.get("answer") for s in fractal.get("sub_answers", [])]
    trace["depths"] = fractal.get("depths_explored", 0)
    stages.append({"stage": "fractal", "elapsed_ms": 0, "served": bool(trace["sub_answers"]),
                   "depths": trace["depths"]})

    # 4. fingerprint: sample the agent's thinking signature
    fp = cognition_fingerprint.cognition_fingerprint_handler(
        {"action": "sample", "agent": agent, "model": model})
    signature = (fp.get("fingerprint") or {})
    trace["signature"] = {k: signature.get(k) for k in ("verbosity", "neologism", "depth") if k in signature}
    stages.append({"stage": "fingerprint", "elapsed_ms": 0, "served": signature.get("served", False)})

    # 5. meter: record the ritual's consultations against the spend ledger
    try:
        oracle_meter.oracle_meter_handler(
            {"action": "record", "prompt": f"ritual:{role}:{question[:60]}", "model": model,
             "cost_usd": 0.001, "served": trace["think_served"]})
        oracle_meter.oracle_meter_handler(
            {"action": "record", "prompt": f"ritual-critique:{role}:{question[:40]}", "model": model,
             "cost_usd": 0.001, "served": bool(stages[1].get("served"))})
    except Exception as e:  # noqa: BLE001 - metering must never sink the ritual
        trace["meter_error"] = str(e)[:80]
    meter = oracle_meter.oracle_meter_handler({"action": "spend"})
    trace["ledger"] = {"consultations": meter.get("usage", {}).get("consultations", 0),
                       "spent_usd": meter.get("budget", {}).get("spent_usd", 0.0)}
    stages.append({"stage": "meter", "elapsed_ms": 0})

    # 6. hexer: bind the whole ritual trace into an immutable artifact
    bound = dream_hexer.dream_hexer_handler(
        {"action": "bind", "text": f"[{role}] {question} :: {answer[:140]} :: {critique[:100]}"})
    artifact = bound.get("dream", {})
    trace["artifact"] = {"hex": artifact.get("hex"), "hex_len": artifact.get("hex_len"),
                         "sha": artifact.get("sha")}
    stages.append({"stage": "hexer", "elapsed_ms": 0})

    return {
        "status": "active",
        "ritual": "Cognition Ritual",
        "agent": agent,
        "role": role,
        "question": question,
        "model": model,
        "trace": trace,
        "stages": stages,
        "total_elapsed_ms": round((time.time() - started) * 1000, 1),
    }


if __name__ == "__main__":
    print(json.dumps(cognition_ritual_handler({"action": "status"}), indent=2))
