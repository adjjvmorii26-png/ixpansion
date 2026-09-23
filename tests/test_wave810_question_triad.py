"""Wave 810 question_triad tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave810_question_triad as w


def test_pipeline():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":810,"name":"question_triad","stage":"question","question":"","roles":{},"hypotheses":[],"experiment":null,"evidence":null,"runs":0,"status":"test"}'
    )
    assert w.handler({"action": "ask", "question": "Does silence scale?"})["status"] == "question_set"
    for role in ("archaeologist", "skeptic", "builder"):
        r = w.handler({"action": "role", "role": role, "text": f"{role} note"})
        assert r["status"] in ("role_recorded", "triad_complete")
    assert w.handler({"action": "status"})["status"] == "triad_complete"
    w.handler({"action": "hypothesize", "hypotheses": ["silence reduces noise"]})
    w.handler({"action": "experiment", "procedure": "A/B caption only", "signal": "lower bounce"})
    w.handler({"action": "evidence", "observed": "bounce -12%"})
    rev = w.handler({"action": "review", "decision": "hold"})
    assert rev["status"] == "review_hold"
    assert rev["audio"] is False
