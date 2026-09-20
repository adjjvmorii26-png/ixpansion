"""Waves 787–789 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave787_dual_track_pr_bot as w787
import wave788_constellation_dashboard_tile as w788
import wave789_entropy_weather_cell as w789


def test_787_classify():
    w787.DATA.mkdir(parents=True, exist_ok=True)
    w787.STATE_FILE.write_text(
        '{"wave":787,"name":"dual_track_pr_bot","classifications":0,"status":"test"}'
    )
    r = w787.handler({"action": "classify", "files": ["api/wave780_x.py", "lab/ops/x.py"]})
    assert r["track"] == "lab"
    assert r["label"] == "track:lab"
    assert r["audio"] is False


def test_788_tile():
    w788.DATA.mkdir(parents=True, exist_ok=True)
    w788.STATE_FILE.write_text(
        '{"wave":788,"name":"constellation_dashboard_tile","renders":0,"status":"test"}'
    )
    r = w788.handler({"action": "tile"})
    assert r["status"] == "tiled"
    assert r["tile"]["hub"] == "ixpansion"
    assert len(r["tile"]["nodes"]) >= 1


def test_789_forecast():
    w789.DATA.mkdir(parents=True, exist_ok=True)
    w789.STATE_FILE.write_text(
        '{"wave":789,"name":"entropy_weather_cell","forecasts":0,"status":"test"}'
    )
    r = w789.handler({"action": "forecast", "text": "aaaaaaaa", "activity": 0.05})
    assert r["weather"] in w789.WEATHERS
    assert r["phase_bias"] in ("solid", "liquid", "gas", "plasma")
    assert r["payload"] is None
