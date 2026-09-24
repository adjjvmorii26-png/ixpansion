"""Wave 817 skillforge_engine tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave817_skillforge_engine as w


def test_pipeline():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":817,"name":"skillforge_engine","stage":"intake","runs":0,"ledger":[],"status":"test"}'
    )
    d = w.handler({"action": "diagram"})
    assert "SKILLFORGE" in d["diagram"][0]
    w.handler({"action": "intake", "skills": ["question-triad"], "builders": ["forge"], "tests": ["t1"]})
    m = w.handler({"action": "mutate", "parent": "question-triad", "variant": "question-triad-v2"})
    assert m["status"] == "mutated"
    L = w.handler({"action": "ledger", "decision": "hold", "note": "needs evidence"})
    assert L["status"] == "ledger_hold"
    assert L["audio"] is False
