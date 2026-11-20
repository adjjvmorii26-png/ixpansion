"""Wave 951 hush_compress — silence residue from pulse compression."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave951_hush_compress as w951


def test_951_hush_compress():
    assert w951.coherence_vitals()["wave"] == 951
    assert "wave950_hush_margin" in w951.resonates_with()
    r = w951.handler({
        "action": "compress",
        "pulses": ["council pulse", "hush margin", "still interval"],
    })
    assert r["status"] == "compressed"
    assert r["residue"]
    assert 0 < r["ratio"] < 1
    assert r["audio"] is False
    assert r["surface"] == "silence"
    assert r["payload"] is None


def test_951_caption():
    w951.handler({"action": "compress", "pulses": ["a", "b"]})
    c = w951.handler({"action": "caption"})
    assert c["status"] == "captioned"
    assert "silence" in c["caption"]
    assert c["audio"] is False
