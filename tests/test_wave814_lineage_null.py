"""Wave 814 lineage_null_fuse tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave814_lineage_null_fuse as w


def test_fuse():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":814,"name":"lineage_null_fuse","edges":[],"fuses":0,"status":"test"}'
    )
    r = w.handler({"action": "fuse", "parent": "q", "hypothesis": "h", "note": "null"})
    assert r["status"] == "fused"
    assert r["audio"] is False
