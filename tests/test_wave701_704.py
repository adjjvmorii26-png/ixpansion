"""Lab evolution 701–704."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave701_still_compound as w701
import wave702_import_quarantine as w702
import wave703_proof_delta as w703
import wave704_lab_epoch_seal as w704

def test_701_still_compound():
    assert w701.coherence_vitals()["wave"] == 701
    r = w701.handler({"action": "tick_still", "seconds": 10})
    assert r["status"] == "compounded" and r["principal"] > 0

def test_702_import_quarantine():
    assert w702.coherence_vitals()["wave"] == 702
    r = w702.handler({"action": "purge"})
    assert r["status"] == "purged"

def test_703_proof_delta():
    assert w703.coherence_vitals()["wave"] == 703
    a = w703.handler({"action": "observe", "fp": "abc" * 10})
    assert a["status"] in ("delta", "unchanged")
    b = w703.handler({"action": "observe", "fp": "abc" * 10})
    assert b["changed"] is False
    c = w703.handler({"action": "observe", "fp": "def" * 10})
    assert c["changed"] is True

def test_704_epoch_seal():
    assert w704.coherence_vitals()["wave"] == 704
    r = w704.handler({"action": "seal", "label": "lab_burst_701_704", "lo": 701, "hi": 704})
    assert r["status"] == "sealed" and r["epoch"]["label"] == "lab_burst_701_704"
