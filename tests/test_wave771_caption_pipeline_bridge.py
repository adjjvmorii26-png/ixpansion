"""Wave 771 caption_pipeline_bridge tests."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave771_caption_pipeline_bridge as w771


def setup_function(_fn=None):
    w771.DATA.mkdir(parents=True, exist_ok=True)
    w771.STATE_FILE.write_text(json.dumps({
        "wave": 771, "name": "caption_pipeline_bridge",
        "exports": 0, "last_path": None, "status": "test",
    }))


def test_contract():
    v = w771.coherence_vitals()
    assert v["wave"] == 771
    assert v["surface"] == "silence"
    assert "wave770_copilot_council_pulse" in w771.resonates_with()


def test_export_silent():
    setup_function()
    r = w771.handler({"action": "export", "frames": ["hook", "core", "cta"]})
    assert r["status"] == "exported"
    assert r["audio"] is False
    assert r["payload"] is None
    path = ROOT / r["path"]
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["audio"] is False
    assert data["style"] == "silent_caption_only"
    assert len(data["frames"]) == 3
