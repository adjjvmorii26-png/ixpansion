"""Wave 818 skillforge_stack_bridge tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave818_skillforge_stack_bridge as w


def test_bridge():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":818,"name":"skillforge_stack_bridge","bridges":0,"status":"test"}'
    )
    r = w.handler({"action": "bridge", "parent": "question-triad"})
    assert r["status"] == "bridged"
    assert r["audio"] is False
