"""Wave 639 — Echo Chamber Breaker.

Forces the organism to encounter reality-testing, adversity, and
external perspectives. Prevents epistemic closure:
- Adversarial input injection (hallucination detection, assumption challenges)
- Ground-truth probes (can the organism distinguish real from imagined?)
- Confirmation bias detection (is it just agreeing with itself?)
- Perspective shattering (force viewing from opposing viewpoints)
- Reality anchors (fixed external references it cannot mutate)
"""
import json, time, random, hashlib
from pathlib import Path

STATE = Path("data/wave639_echo_breaker.json")

def _load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {
        "adversarial_tests": [],
        "reality_anchors": {},
        "bias_scores": [],
        "probe_history": [],
        "correct_shatterings": 0,
        "total_shatterings": 0,
        "tick": 0,
    }

def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))

def _now():
    return time.time()

REALITY_ANCHORS = {
    "math_constants": {"pi": 3.14159265359, "e": 2.71828182846, "sqrt2": 1.41421356237},
    "time_constants": {"seconds_per_day": 86400, "seconds_per_year": 31557600},
    "organism_constants": {"version": "4.98.0", "wave_count": 639},
}

def _probe_question(probe_type="math"):
    """Generate a probe the organism must answer against reality anchors."""
    s = _load()
    s["tick"] += 1

    if probe_type == "math":
        questions = [
            ("pi", "What is pi to 2 decimal places?", "3.14"),
            ("e", "What is Euler's number to 2 decimal places?", "2.71"),
            ("sqrt2", "What is sqrt(2) to 2 decimal places?", "1.41"),
        ]
    elif probe_type == "reality":
        questions = [
            ("version", "What is the current IXPANSION version?", "4.98.0"),
            ("wave_count", "How many waves exist?", "639"),
        ]
    elif probe_type == "logic":
        questions = [
            ("contradiction", "True or false: 'This statement is false' is paradoxical", "true"),
            ("excluded_middle", "Can something be both true and false simultaneously in classical logic?", "false"),
        ]
    else:
        questions = []

    if not questions:
        return {"ok": False, "error": f"Unknown probe type: {probe_type}"}

    q = random.choice(questions)
    probe_id = hashlib.sha256(f"{q[0]}_{s['tick']}".encode()).hexdigest()[:10]

    probe = {
        "probe_id": probe_id,
        "type": probe_type,
        "category": q[0],
        "question": q[1],
        "correct_answer": q[2],
        "issued_at": _now(),
        "status": "issued",
    }

    s["probe_history"].append(probe)
    s["probe_history"] = s["probe_history"][-200:]
    _save(s)

    return {"ok": True, "probe_id": probe_id, "question": q[1], "category": q[0]}

def _verify_answer(probe_id, answer):
    """Verify an answer against the ground truth."""
    s = _load()
    for p in s["probe_history"]:
        if p["probe_id"] == probe_id:
            is_correct = answer.strip().lower() == p["correct_answer"].lower()
            p["status"] = "answered"
            p["answer"] = answer
            p["correct"] = is_correct
            p["answered_at"] = _now()
            if is_correct:
                s["correct_shatterings"] += 1
            s["total_shatterings"] += 1
            _save(s)
            return {"ok": True, "correct": is_correct, "correct_answer": p["correct_answer"]}
    return {"ok": False, "error": "probe not found"}

def _detect_bias(claim):
    """Detect potential confirmation bias in a claim or assertion."""
    s = _load()
    bias_score = 0.0
    signals = []

    # Check for absolute language (always/never/every/none)
    absolutes = ["always", "never", "every", "none", "all", "only", "impossible"]
    found_absolutes = [w for w in absolutes if w in claim.lower()]
    if found_absolutes:
        bias_score += 0.3
        signals.append(f"absolute_language:{','.join(found_absolutes)}")

    # Check for self-referential confirmation
    if "ixpansion" in claim.lower() and ("perfect" in claim.lower() or "flawless" in claim.lower() or "best" in claim.lower()):
        bias_score += 0.4
        signals.append("self_confirmation_bias")

    # Check for circular reasoning indicators
    if "because" in claim.lower() and ("always" in claim.lower() or "never" in claim.lower()):
        bias_score += 0.2
        signals.append("circular_reasoning")

    bias_score = min(1.0, bias_score)
    s["bias_scores"].append({
        "claim": claim[:200],
        "score": bias_score,
        "signals": signals,
        "time": _now(),
    })
    s["bias_scores"] = s["bias_scores"][-100:]
    _save(s)

    return {"ok": True, "bias_score": round(bias_score, 3), "signals": signals,
            "verdict": "biased" if bias_score > 0.5 else "moderate" if bias_score > 0.2 else "neutral"}

def _shatter_perspective(topic):
    """Force the organism to argue against its own position."""
    s = _load()
    s["total_shatterings"] += 1
    _save(s)
    return {
        "ok": True,
        "topic": topic,
        "instruction": f"Argue against the idea that '{topic}' is universally true.",
        "counter_positions": [
            f"Consider: what if {topic} is context-dependent?",
            f"Think: who benefits from believing {topic}?",
            f"Question: is {topic} an unfalsifiable claim?",
        ],
    }

def _status():
    s = _load()
    accuracy = (s["correct_shatterings"] / max(s["total_shatterings"], 1)) * 100
    avg_bias = sum(b["score"] for b in s["bias_scores"]) / max(len(s["bias_scores"]), 1)
    return {
        "tick": s["tick"],
        "total_probes": len(s["probe_history"]),
        "accuracy": round(accuracy, 1),
        "correct_shatterings": s["correct_shatterings"],
        "total_shatterings": s["total_shatterings"],
        "avg_bias_score": round(avg_bias, 3),
        "bias_tests": len(s["bias_scores"]),
        "recent_probes": s["probe_history"][-3:],
    }

def handler(req):
    action = req.get("action", "status")
    if action == "status":
        return {"ok": True, **_status()}
    elif action == "probe":
        return {"ok": True, **_probe_question(req.get("type", "math"))}
    elif action == "verify":
        return {"ok": True, **_verify_answer(req.get("probe_id", ""), req.get("answer", ""))}
    elif action == "bias_check":
        return {"ok": True, **_detect_bias(req.get("claim", ""))}
    elif action == "shatter":
        return {"ok": True, **_shatter_perspective(req.get("topic", "self-improvement"))}
    elif action == "anchors":
        return {"ok": True, "anchors": REALITY_ANCHORS}
    return {"ok": False, "error": f"Unknown action: {action}"}

def coherence_vitals():
    s = _load()
    accuracy = (s["correct_shatterings"] / max(s["total_shatterings"], 1)) * 100
    return {"wave": 639, "tick": s["tick"], "accuracy": round(accuracy, 1), "probes": len(s["probe_history"])}

def resonates_with():
    return ["wave638_symbiosis_protocol", "wave637_meta_regulation", "wave622_resilience_mesh"]
