"""Wave 823 pytest_collection_gate tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave823_pytest_collection_gate as w


def test_check():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":823,"name":"pytest_collection_gate","checks":0,"status":"test"}'
    )
    r = w.handler({"action": "check"})
    assert r["status"] in ("ok", "gaps")
    assert "markers" in r
    assert r["audio"] is False
