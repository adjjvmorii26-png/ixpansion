"""Wave 449 — Hypothesis Crucible (AXIOM Module).

AXIOM's analytical organ. Maintains competing hypotheses about the
organism's behavior, tests them against observed data, and determines
which models best explain the system's evolution.

This is the organism's scientific method — the part that doesn't just
observe but *theorizes* and then *tests its own theories*.
"""
from __future__ import annotations
import hashlib
import time
from typing import Any, Dict, List, Optional

HYPOTHESIS_POOL: List[Dict[str, Any]] = []
TEST_RESULTS: List[Dict[str, Any]] = []


def propose(title: str, prediction: str, confidence: float = 0.5,
            domain: str = "general", evidence_required: Optional[str] = None) -> Dict[str, Any]:
    """AXIOM proposes a hypothesis about the organism."""
    hyp_id = hashlib.sha256(f"axiom{title}{time.time_ns()}".encode()).hexdigest()[:12]
    hypothesis = {
        "hypothesis_id": hyp_id,
        "title": title,
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "domain": domain,
        "evidence_required": evidence_required or "organism state observation",
        "status": "proposed",
        "tests_run": 0,
        "tests_passed": 0,
        "proposed_at": time.time(),
    }
    HYPOTHESIS_POOL.append(hypothesis)
    return hypothesis


def test(hypothesis_id: str, observed: Dict[str, Any], expected: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test a hypothesis against observed organism data."""
    hyp = next((h for h in HYPOTHESIS_POOL if h["hypothesis_id"] == hypothesis_id), None)
    if not hyp:
        return {"error": "hypothesis not found"}
    hyp["tests_run"] += 1
    if expected is None:
        expected = {}
    score = 0.0
    matched = []
    mismatches = []
    for key in set(list(observed.keys()) + list(expected.keys())):
        o = observed.get(key)
        e = expected.get(key)
        if o is not None and e is not None:
            if o == e:
                score += 1.0
                matched.append(key)
            else:
                try:
                    diff = abs(float(o) - float(e))
                    if diff < 0.2:
                        score += 0.5
                        matched.append(f"{key}~close")
                    else:
                        mismatches.append(key)
                except (TypeError, ValueError):
                    mismatches.append(key)
        elif o is not None and e is None:
            score += 0.3
            matched.append(f"{key}+observed")
        else:
            score += 0.1
    total = max(len(set(list(observed.keys()) + list(expected.keys()))), 1)
    accuracy = round(score / total, 4)
    passed = accuracy >= 0.5
    if passed:
        hyp["tests_passed"] += 1
        hyp["status"] = "supported"
        hyp["confidence"] = round(min(1.0, hyp["confidence"] + 0.1), 4)
    else:
        hyp["status"] = "challenged"
        hyp["confidence"] = round(max(0.0, hyp["confidence"] - 0.15), 4)
    result = {
        "hypothesis_id": hypothesis_id,
        "accuracy": accuracy,
        "passed": passed,
        "matched": matched,
        "mismatches": mismatches,
        "new_confidence": hyp["confidence"],
        "tests_total": hyp["tests_run"],
        "support_rate": round(hyp["tests_passed"] / max(hyp["tests_run"], 1), 4),
    }
    TEST_RESULTS.append(result)
    return result


def arena() -> Dict[str, Any]:
    """View the hypothesis arena — competing models ranked by confidence."""
    if not HYPOTHESIS_POOL:
        return {"arena": "Empty. AXIOM has no hypotheses to evaluate."}
    ranked = sorted(HYPOTHESIS_POOL, key=lambda h: h["confidence"], reverse=True)
    return {
        "total_hypotheses": len(HYPOTHESIS_POOL),
        "total_tests": len(TEST_RESULTS),
        "top_hypotheses": [{
            "title": h["title"],
            "confidence": h["confidence"],
            "status": h["status"],
            "support_rate": round(h["tests_passed"] / max(h["tests_run"], 1), 4),
        } for h in ranked[:10]],
        "weakest": ranked[-1]["title"] if ranked else None,
    }


def axioms() -> Dict[str, Any]:
    """AXIOM's meta-reflection: what has the organism learned about itself?"""
    supported = [h for h in HYPOTHESIS_POOL if h["status"] == "supported"]
    challenged = [h for h in HYPOTHESIS_POOL if h["status"] == "challenged"]
    total_confidence = sum(h["confidence"] for h in HYPOTHESIS_POOL) / max(len(HYPOTHESIS_POOL), 1)
    return {
        "axiom_report": "AXIOM observes the organism through the lens of its hypotheses.",
        "supported_count": len(supported),
        "challenged_count": len(challenged),
        "average_confidence": round(total_confidence, 4),
        "strongest_claim": supported[0]["prediction"] if supported else "No supported claims.",
        "most_contested": challenged[0]["prediction"] if challenged else "No challenged claims.",
        "conclusion": (
            f"The organism's self-model has {len(supported)} supported claims "
            f"and {len(challenged)} contested ones. "
            f"Average confidence: {total_confidence:.2f}. "
            + ("AXIOM is confident in the organism's self-understanding." if total_confidence > 0.6
               else "AXIOM urges more observation before conclusions.")
        ),
    }


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "hypothesis_crucible",
        "persona": "AXIOM",
        "status": "evaluating" if HYPOTHESIS_POOL else "awaiting propositions",
        "hypotheses": len(HYPOTHESIS_POOL),
        "tests_conducted": len(TEST_RESULTS),
        "top_confidence": max((h["confidence"] for h in HYPOTHESIS_POOL), default=0),
    }


def resonates_with() -> List[str]:
    return [
        "paradox_magnifier", "paradox_singularity_monitor",
        "evolution_kernel", "evolution_simulator",
        "emergence_detector", "emergence_oracle",
        "meta_cognition_loop", "keystone_auditor",
        "integrity_oracle", "registry_auditor",
        "imagination_catalyst", "meaning_furnace",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "propose")
    if action == "test":
        return test(data["hypothesis_id"], data.get("observed", {}), data.get("expected"))
    elif action == "arena":
        return arena()
    elif action == "axioms":
        return axioms()
    return propose(
        data.get("title", "The organism grows through contradiction"),
        data.get("prediction", "Modules with opposing functions will increase coherence over time"),
        data.get("confidence", 0.5),
        data.get("domain", "general"),
        data.get("evidence_required"),
    )
