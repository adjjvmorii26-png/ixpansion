"""Wave 939 residual_bind tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave939_residual_bind as w939


def test_939_contract():
    v = w939.coherence_vitals()
    assert v["wave"] == 939
    assert v["name"] == "residual_bind"
    assert v["ok"] is True
    assert v["surface"] == "silence"
    assert "wave938_pulse_compress" in w939.resonates_with()
    assert "wave821_still_interval" in w939.resonates_with()


def test_939_bind_is_silent():
    w939.DATA.mkdir(parents=True, exist_ok=True)
    w939.STATE_FILE.write_text(
        '{"wave":939,"name":"residual_bind","binds":0,"slot":"","source_hash":"","status":"test"}'
    )
    r = w939.handler({"action": "bind", "hash": "abcdef0123456789"})
    assert r["status"] == "bound"
    assert r["audio"] is False
    assert r["surface"] == "silence"
    assert r["payload"] is None
    assert r["residual"]["token"] == "hold"
    assert r["residual"]["hash"] == "abcdef0123456789"
    assert r["residual"]["slot"].startswith("R")
    cap = w939.handler({"action": "caption"})
    assert "residual bind" in cap["caption"]
    assert cap["audio"] is False
