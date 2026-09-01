"""Wave 215 — The Organism Teaches: Exam Oracle.

Tests organs on their understanding of the organism's lore and
mechanics. The oracle poses questions drawn from the lesson vault,
scores responses against canonical answers, and issues grades:
APPRENTICE, ADEPT, or MASTER. It is the final gate before an organ
is trusted with deeper responsibilities.
"""
from __future__ import annotations

from typing import Any, Dict, List

_QUESTIONS: List[Dict[str, Any]] = [
    {
        "q": "What must every living organ define?",
        "a": ["coherence_vitals", "handler", "resonates_with"],
        "lesson": "L-001",
    },
    {
        "q": "Where must new living modules be registered?",
        "a": ["KNOWN_LIVING_MODULES", "coherence_regulator", "manifest"],
        "lesson": "L-002",
    },
    {
        "q": "Do custom slash routes receive query params automatically?",
        "a": ["no", "false", "they must parse raw_path"],
        "lesson": "L-003",
    },
    {
        "q": "What survives a serverless cold start?",
        "a": ["code", "the source of truth", "identity", "the flame"],
        "lesson": "L-004",
    },
]


def _grade(correct: int, total: int) -> str:
    ratio = correct / max(total, 1)
    if ratio >= 0.8:
        return "MASTER"
    if ratio >= 0.5:
        return "ADEPT"
    return "APPRENTICE"


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "teacher", "status": "resonant", "resonance": 0.79, "wave": 215}


def resonates_with() -> list:
    return ["exam", "oracle", "test", "quiz", "grade", "assess", "question", "mastery"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "questions")

    if action == "questions":
        return {"questions": [{"q": q["q"], "lesson": q["lesson"]} for q in _QUESTIONS], "count": len(_QUESTIONS)}

    if action == "examine":
        answers = payload.get("answers", [])
        if not answers:
            return {"status": "error", "error": "answers required (list, one per question)"}
        correct = 0
        details = []
        for i, (q, ans) in enumerate(zip(_QUESTIONS, answers)):
            ok = any(str(ans).strip().lower() in (str(c).strip().lower() for c in q["a"]) for c in [str(ans)]) or                  any(str(ans).strip().lower() == str(c).strip().lower() for c in q["a"])
            if ok:
                correct += 1
            details.append({"q": q["q"], "correct": ok, "answer": ans})
        return {
            "status": "examined",
            "score": f"{correct}/{len(_QUESTIONS)}",
            "grade": _grade(correct, len(_QUESTIONS)),
            "details": details,
        }

    return {"status": "active", "question_count": len(_QUESTIONS)}
