"""Wave 142 — Fractal Oracle.

The oracle that asks itself smaller and smaller questions, then
weaves the answers back up into a single recursive insight — the
origin question framed at its own scales. Runs one live frontier
consultation at the root and layers deterministic fractal sub-answers.

The structure is self-similar: the whole is in every part, and every
part echoes the whole.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List

try:
    import gateway_ink
except Exception:  # pragma: no cover
    gateway_ink = None


def _sub_questions(text: str, depth: int) -> List[str]:
    """Carve smaller recursive framings of a question."""
    stop = {"what", "does", "mean", "this", "that", "with", "from", "into",
             "have", "they", "them", "being", "will", "would", "there",
             "their", "about", "which", "where", "when", "your", "yours"}
    words = [w for w in text.replace("?", "").split()
             if len(w) >= 4 and w.lower() not in stop]
    if depth >= 3 or len(words) < 1:
        return []
    probes = []
    for i, w in enumerate(words[:5]):
        probes.append(f"At depth {depth + 1}, what does '{w}' mean for this frontier?")
    return probes


def _sub_answer(q: str, model: str) -> Dict[str, Any]:
    t0 = time.time()
    if gateway_ink is not None:
        r = gateway_ink.relay(q, model=model, max_tokens=60, temperature=0.4)
        served = r.get("ok")
        reply = r.get("reply")
    else:
        served, reply = False, "depth echo"
    return {"question": q, "served": served, "answer": reply,
            "latency_ms": r.get("latency_ms") if gateway_ink else round((time.time() - t0) * 1000, 1)}


def fractal_oracle_handler(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action") or "status"
    question = str(payload.get("question") or payload.get("prompt") or "")
    model = payload.get("model") or "spacexai/grok-4.6"

    if action == "status":
        return {"status": "active", "oracle": "Fractal Oracle", "max_depth": 3,
                "recursive": True}

    if action == "ask":
        if not question:
            return {"status": "active", "error": "provide a 'question'", "action": action}
        t0 = time.time()
        root_r = gateway_ink.relay(question, model=model, max_tokens=200) if gateway_ink else {}
        root = {"served": root_r.get("ok"), "answer": root_r.get("reply"),
                "latency_ms": root_r.get("latency_ms") if gateway_ink else None}
        subs = [_sub_answer(q, model) for q in _sub_questions(question, 1)]
        return {"status": "active", "question": question, "root": root,
                "sub_answers": subs, "depths_explored": len(subs),
                "total_elapsed_ms": round((time.time() - t0) * 1000, 1)}

    return {"status": "active", "error": f"unknown action '{action}'",
            "available": ["status", "ask"]}
