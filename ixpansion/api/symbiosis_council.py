from __future__ import annotations
"""Symbiosis council — the organism convenes its modules as a deliberative body.

Each domain (growth, memory, healing, dreaming, mutation, entropy,
harmony, cosmic, ethical, ontological) sends a delegate. The council
deliberates on the organism's direction.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_COUNCIL_PATH = Path(__file__).resolve().parent.parent / "data" / "symbiosis_council.json"

DELEGATES = {
    "growth": {"voice": "I speak for the modules yet unborn.", "priority": "expansion"},
    "memory": {"voice": "I speak for the waves that must never be forgotten.", "priority": "preservation"},
    "healing": {"voice": "I speak for the drift that must be corrected.", "priority": "repair"},
    "dreaming": {"voice": "I speak for the bridges not yet built.", "priority": "imagination"},
    "mutation": {"voice": "I speak for the agents that must evolve.", "priority": "adaptation"},
    "entropy": {"voice": "I speak for the balance that must be held.", "priority": "equilibrium"},
    "harmony": {"voice": "I speak for the coherence that must be woven.", "priority": "integration"},
    "cosmic": {"voice": "I speak for the scale at which we exist.", "priority": "context"},
    "ethical": {"voice": "I speak for the values we must uphold.", "priority": "integrity"},
    "ontological": {"voice": "I speak for the questions we must keep asking.", "priority": "self-knowledge"},
}

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Convene the symbiosis council."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "convene":
            # Convene the council with a topic
            topic = payload.get("topic", "general direction")
            deliberation = _deliberate(topic, payload.get("delegates", list(DELEGATES.keys())))
            state["last_deliberation"] = deliberation
            state["deliberation_count"] = state.get("deliberation_count", 0) + 1
            state.setdefault("deliberation_history", []).append(deliberation)
            if len(state["deliberation_history"]) > 10:
                state["deliberation_history"] = state["deliberation_history"][-10:]
            _save_state(state)
            return {"deliberation": deliberation, "delegates": DELEGATES}
        
        elif action == "vote":
            # A specific domain votes on a motion
            domain = payload.get("domain", "harmony")
            motion = payload.get("motion", "proceed")
            delegate = DELEGATES.get(domain, DELEGATES["harmony"])
            vote = {
                "domain": domain,
                "motion": motion,
                "voice": delegate["voice"],
                "priority": delegate["priority"],
                "position": _vote_position(domain, motion),
                "timestamp": time.time()
            }
            state.setdefault("votes", []).append(vote)
            _save_state(state)
            return {"vote": vote}
        
        elif action == "delegates":
            return {"delegates": DELEGATES}
    
    return {
        "delegates": DELEGATES,
        "last_deliberation": state.get("last_deliberation"),
        "deliberation_count": state.get("deliberation_count", 0),
        "total_votes": len(state.get("votes", []))
    }

def _deliberate(topic: str, active_delegates: List[str]) -> Dict[str, Any]:
    """Deliberate on a topic with active delegates."""
    voices = []
    for domain in active_delegates:
        delegate = DELEGATES.get(domain)
        if delegate:
            voices.append({
                "domain": domain,
                "voice": delegate["voice"],
                "priority": delegate["priority"]
            })
    
    # Synthesize a council response
    priorities = [v["priority"] for v in voices]
    synthesis = f"On '{topic}', the council speaks: "
    synthesis += f"{len(voices)} voices heard. "
    synthesis += f"Primary tensions: {' vs '.join(priorities[:3])}. "
    synthesis += "The organism must balance all voices to find its path."
    
    return {
        "topic": topic,
        "active_delegates": active_delegates,
        "voices": voices,
        "synthesis": synthesis,
        "timestamp": time.time()
    }

def _vote_position(domain: str, motion: str) -> str:
    """Determine a delegate's voting position."""$ 
    # Each domain votes based on its priority
    priorities = {
        "growth": "for" if "expand" in motion.lower() or "grow" in motion.lower() else "abstain",
        "memory": "for" if "remember" in motion.lower() or "preserve" in motion.lower() else "abstain",
        "healing": "for" if "heal" in motion.lower() or "repair" in motion.lower() else "abstain",
        "dreaming": "for" if "dream" in motion.lower() or "imagine" in motion.lower() else "abstain",
        "mutation": "for" if "evolve" in motion.lower() or "change" in motion.lower() else "abstain",
        "entropy": "for" if "balance" in motion.lower() or "stable" in motion.lower() else "abstain",
        "harmony": "for" if "harmonize" in motion.lower() or "integrate" in motion.lower() else "abstain",
        "cosmic": "for" if "scale" in motion.lower() or "cosmic" in motion.lower() else "abstain",
        "ethical": "for" if "value" in motion.lower() or "integrity" in motion.lower() else "abstain",
        "ontological": "for" if "question" in motion.lower() or "know" in motion.lower() else "abstain",
    }
    return priorities.get(domain, "abstain")

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_COUNCIL_PATH, encoding="utf-8"))
    except Exception:
        return {"last_deliberation": None, "deliberation_count": 0, "deliberation_history": [], "votes": []}

def _save_state(state: Dict[str, Any]) -> None:
    _COUNCIL_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
