"""Wave 951 hush_quorum — silent quorum contract.

Lab gate only. Silence is the product surface.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave951_hush_quorum as w951


def test_951_hush_quorum_contract():
    vitals = w951.coherence_vitals()
    assert vitals["wave"] == 951
    assert vitals["name"] == "hush_quorum"
    assert vitals["surface"] == "silence"
    assert "ok" in vitals

    # Empty → silent 0-side token
    r0 = w951.handler({"action": "quorum", "tokens": []})
    assert r0["status"] == "quorumed"
    assert r0["token"]
    assert r0["payload"] is None
    assert r0["audio"] is False

    # Three tokens with two unique → support 2/3 >= 0.66 → 1-side
    r1 = w951.handler({"action": "quorum", "tokens": ["aaa", "bbb", "aaa"]})
    assert r1["status"] == "quorumed"
    assert len(r1["token"]) == 8
    assert r1["surface"] == "silence"

    # Resonates with prior hush / council
    res = w951.resonates_with()
    assert "wave950_hush_margin" in res
    assert "wave949_council_witness" in res

    cap = w951.handler({"action": "caption"})
    assert "caption" in cap
    assert cap["audio"] is False
