"""Lab test for wave 953 memory_compress. Silence surface, compression as memory."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave953_memory_compress as w953


def test_wave953_vitals_and_contract():
    v = w953.coherence_vitals()
    assert v["wave"] == 953
    assert v["name"] == "memory_compress"
    assert v["surface"] == "silence"
    assert v["ok"] is True
    assert callable(w953.resonates_with)
    assert "wave952_silence_seed" in w953.resonates_with()


def test_wave953_compress_and_caption():
    r = w953.handler({"action": "compress", "seed": "council_residue"})
    assert r["status"] == "compressed"
    assert "residue" in r
    assert len(r["residue"]) == 12
    assert r["audio"] is False
    assert r["surface"] == "silence"
    c = w953.handler({"action": "caption"})
    assert c["status"] == "captioned"
    assert "caption" in c
    assert c["audio"] is False
