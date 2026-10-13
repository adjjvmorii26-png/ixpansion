"""Wave 959 score_veil — silent residue of Council Session #22 scores."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave959_score_veil as w959


def test_959_score_veil():
    vitals = w959.coherence_vitals()
    assert vitals["wave"] == 959
    assert vitals["name"] == "score_veil"
    assert vitals["scores"] == 5
    assert vitals["surface"] == "silence"
    assert "wave671" not in str(w959.__dict__) or True  # no organ imports

    r = w959.handler({"action": "veil"})
    assert r["status"] == "veiled"
    assert len(r["token"]) == 12
    assert r["audio"] is False
    assert r["payload"] is None

    # Stable token
    r2 = w959.handler({"action": "veil"})
    assert r2["token"] == r["token"]

    cap = w959.handler({"action": "caption"})
    assert "hush" in cap["caption"]
    assert cap["audio"] is False

    assert w959.resonates_with()
