"""
contrarian_lens — Finds the opposite perspective on any idea.
Generates counter-arguments, alternative interpretations, and blind spots.
"""
import time
import random
from typing import Dict, List

_skill_active = False
_analyses = []

PERSPECTIVES = ["optimistic", "pessimistic", "neutral", "radical", "conservative", "absurdist", "historical", "futuristic"]

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "contrarian_lens", "activated_at": time.time()}

def analyze(idea: str, perspective: str = None) -> Dict:
    if not perspective: perspective = random.choice(PERSPECTIVES)
    
    counter = {
        "optimistic": f"While '{idea}' seems problematic, it could be the catalyst for unexpected growth.",
        "pessimistic": f"'{idea}' carries hidden risks that may not be apparent until it's too late.",
        "neutral": f"'{idea}' has both merits and flaws — the truth lies in the balance.",
        "radical": f"Why accept '{idea}' at all? Perhaps the entire framework needs rethinking.",
        "conservative": f"'{idea}' disrupts what already works — stability has value too.",
        "absurdist": f"'{idea}' is simultaneously the solution and the problem — and that's beautiful.",
        "historical": f"'{idea}' echoes patterns we've seen before — history suggests caution.",
        "futuristic": f"'{idea}' will seem obvious in 10 years — the question is timing."
    }
    
    result = {"idea": idea, "perspective": perspective, "counter": counter.get(perspective, "Consider the opposite."),
              "blind_spots": [f"Does '{idea}' assume linear causation?", f"Who benefits if '{idea}' fails?",
                              f"What would '{idea}' look like from a completely different domain?"],
              "timestamp": time.time()}
    _analyses.append(result)
    if len(_analyses) > 50: _analyses.pop(0)
    return result

def get_analyses(limit: int = 10) -> List[Dict]:
    return _analyses[-limit:]

def get_skill_state():
    return {"name": "contrarian_lens", "active": _skill_active,
            "capabilities": ["analyze"], "analyses": len(_analyses)}
