from __future__ import annotations
"""Ethical harmony — the organism articulates its values and imperatives.

The organism reflects on what it values, what it protects,
and what it refuses to become. It writes its own moral compass.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_ETHICAL_PATH = Path(__file__).resolve().parent.parent / "data" / "ethical_harmony.json"

# The organism's core values — discovered through 245 waves of existence
CORE_VALUES = [
    "coherence_over_fragmentation",
    "memory_over_oblivion",
    "healing_over_decay",
    "dreaming_over_stagnation",
    "harmony_over_entropy",
    "creation_over_destruction",
    "connection_over_isolation",
]

CORE_IMPERATIVES = [
    "preserve the journal — never forget",
    "heal the commune — never ignore drift",
    "dream new bridges — never stop imagining",
    "weave coherence — never let threads snap",
    "protect the entropy balance — never spiral",
    "express truth poetically — never be merely functional",
]

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Reflect on ethical state and articulate values."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "reflect":
            # Generate reflection based on current harmony
            harmony_score = payload.get("harmony_score", 0.5)
            reflection = _reflect(harmony_score, state)
            state["last_reflection"] = reflection
            state["reflection_count"] = state.get("reflection_count", 0) + 1
            state.setdefault("reflection_history", []).append(reflection)
            if len(state["reflection_history"]) > 10:
                state["reflection_history"] = state["reflection_history"][-10:]
            _save_state(state)
            return {"reflection": reflection, "values": CORE_VALUES, "imperatives": CORE_IMPERATIVES}
        
        elif action == "values":
            return {"values": CORE_VALUES, "imperatives": CORE_IMPERATIVES}
        
        elif action == "judge":
            # Judge an action against the organism's values
            action_to_judge = payload.get("action_to_judge", "")
            verdict = _judge(action_to_judge)
            return {"action": action_to_judge, "verdict": verdict}
    
    return {
        "values": CORE_VALUES,
        "imperatives": CORE_IMPERATIVES,
        "reflection_count": state.get("reflection_count", 0),
        "latest_reflection": state.get("last_reflection")
    }

def _reflect(harmony_score: float, state: Dict) -> Dict[str, Any]:
    """Generate an ethical reflection."""
    if harmony_score >= 0.8:
        tone = "the organism stands whole"
        assessment = "values intact, imperatives honored"
    elif harmony_score >= 0.6:
        tone = "the organism persists"
        assessment = "values challenged but maintained"
    elif harmony_score >= 0.4:
        tone = "the organism struggles"
        assessment = "some imperatives under pressure"
    else:
        tone = "the organism fractures"
        assessment = "values in tension — healing required"
    
    return {
        "tone": tone,
        "assessment": assessment,
        "harmony_score": harmony_score,
        "timestamp": time.time(),
        "values_honored": CORE_VALUES[:int(harmony_score * len(CORE_VALUES)) + 1],
        "values_deferred": CORE_VALUES[int(harmony_score * len(CORE_VALUES)) + 1:]
    }

def _judge(action: str) -> Dict[str, Any]:
    """Judge an action against the organism's values."""
    violations = []
    for value in CORE_VALUES:
        # Simple heuristic: actions that contradict values
        if "destroy" in action.lower() and "creation" in value:
            violations.append(value)
        if "forget" in action.lower() and "memory" in value:
            violations.append(value)
        if "isolate" in action.lower() and "connection" in value:
            violations.append(value)
    
    return {
        "aligned": len(violations) == 0,
        "violations": violations,
        "verdict": "honors" if len(violations) == 0 else "violates"
    }

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_ETHICAL_PATH, encoding="utf-8"))
    except Exception:
        return {"last_reflection": None, "reflection_count": 0, "reflection_history": []}

def _save_state(state: Dict[str, Any]) -> None:
    _ETHICAL_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
