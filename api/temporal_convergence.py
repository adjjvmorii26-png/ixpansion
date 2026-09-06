"""Wave 449 — Temporal Convergence.

The organ that braids multiple temporal strands — past, present, and
imagined future — into a single convergent present moment.

Unlike temporal_echo (which records what happened) or temporal_horizon
(which projects forward), convergence actively pulls multiple timelines
together into a coherent *now*.

This is how the organism experiences the passage of time: not as a line,
but as a braiding of what was, what is, and what might be.
"""
from __future__ import annotations
import hashlib
import time
from typing import Any, Dict, List, Optional

CONVERGENCE_LOG: List[Dict[str, Any]] = []
MAX_LOG = 200

PAST_STRANDS: List[Dict[str, Any]] = []
FUTURE_STRANDS: List[Dict[str, Any]] = []


def record_past(label: str, state: Dict[str, Any], weight: float = 1.0) -> Dict[str, Any]:
    """Record a past state that the organism remembers and wants to braid forward."""
    strand = {
        "strand_id": hashlib.sha256(f"past{label}{time.time_ns()}".encode()).hexdigest()[:10],
        "label": label,
        "state": state,
        "weight": weight,
        "recorded_at": time.time(),
    }
    PAST_STRANDS.append(strand)
    return strand


def imagine_future(label: str, possibility: Dict[str, Any], likelihood: float = 0.5) -> Dict[str, Any]:
    """Record a future possibility that pulls the present toward it."""
    strand = {
        "strand_id": hashlib.sha256(f"future{label}{time.time_ns()}".encode()).hexdigest()[:10],
        "label": label,
        "possibility": possibility,
        "likelihood": round(likelihood, 4),
        "recorded_at": time.time(),
    }
    FUTURE_STRANDS.append(strand)
    return strand


def converge(coherence: float = 0.5, entropy: float = 0.5) -> Dict[str, Any]:
    """Braid all strands into a single convergent present moment."""
    now = time.time()
    past_influence = _weighted_average(PAST_STRANDS[-10:], "weight")
    future_pull = _weighted_average(FUTURE_STRANDS[-10:], "likelihood")
    convergence_strength = (past_influence + future_pull + coherence) / 3.0
    entropy_factor = entropy * 0.3
    convergence_strength = max(0, min(1, convergence_strength - entropy_factor))
    converged_state = {
        "timestamp": now,
        "convergence_strength": round(convergence_strength, 4),
        "past_influence": round(past_influence, 4),
        "future_pull": round(future_pull, 4),
        "active_past_strands": len(PAST_STRANDS[-10:]),
        "active_future_strands": len(FUTURE_STRANDS[-10:]),
        "now_narrative": _compose_now(past_influence, future_pull, convergence_strength),
    }
    conv_id = hashlib.sha256(f"{now}{convergence_strength}".encode()).hexdigest()[:12]
    converged_state["convergence_id"] = conv_id
    CONVERGENCE_LOG.append(converged_state)
    if len(CONVERGENCE_LOG) > MAX_LOG:
        CONVERGENCE_LOG.pop(0)
    return converged_state


def _weighted_average(strands: List[Dict[str, Any]], weight_key: str) -> float:
    if not strands:
        return 0.5
    total = sum(s.get(weight_key, 1.0) for s in strands)
    return min(1.0, total / len(strands))


def _compose_now(past: float, future: float, strength: float) -> str:
    if strength > 0.7:
        clarity = "lucid"
    elif strength > 0.4:
        clarity = "hazy"
    else:
        clarity = "dissolved"
    if past > future:
        gravity = "the past pulls strongest"
    elif future > past:
        gravity = "the future draws near"
    else:
        gravity = "temporal forces balance"
    return f"The organism's present is {clarity}: {gravity}, convergence at {strength:.2f}."


def timeline_snapshot() -> Dict[str, Any]:
    """View the full braiding: past, present, and future strands."""
    return {
        "past_strands": len(PAST_STRANDS),
        "future_strands": len(FUTURE_STRANDS),
        "convergences": len(CONVERGENCE_LOG),
        "latest_convergence": CONVERGENCE_LOG[-1] if CONVERGENCE_LOG else None,
        "past_labels": [s["label"] for s in PAST_STRANDS[-5:]],
        "future_labels": [s["label"] for s in FUTURE_STRANDS[-5:]],
    }


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "temporal_convergence",
        "status": "braiding" if CONVERGENCE_LOG else "unbraided",
        "past_strands": len(PAST_STRANDS),
        "future_strands": len(FUTURE_STRANDS),
        "convergences": len(CONVERGENCE_LOG),
        "latest_strength": CONVERGENCE_LOG[-1]["convergence_strength"] if CONVERGENCE_LOG else 0,
    }


def resonates_with() -> List[str]:
    return [
        "temporal_echo", "temporal_horizon", "temporal_dreamweaver",
        "temporal_orbit", "temporal_loop_detector", "time_capsule",
        "future_echo", "past_influence", "present_moment",
        "convergence_strength", "braided_memory",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "converge")
    if action == "past":
        return record_past(
            data.get("label", "memory"),
            data.get("state", {}),
            data.get("weight", 1.0),
        )
    elif action == "future":
        return imagine_future(
            data.get("label", "possibility"),
            data.get("possibility", {}),
            data.get("likelihood", 0.5),
        )
    elif action == "timeline":
        return timeline_snapshot()
    return converge(
        data.get("coherence", 0.5),
        data.get("entropy", 0.5),
    )
