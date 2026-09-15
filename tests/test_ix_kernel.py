"""IX Kernel enormous leap."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "lab" / "ops"))
sys.path.insert(0, str(ROOT / "api"))

from ix_kernel import ignite, _next_wave_number
import wave707_ix_kernel as w707


def test_next_wave_number():
    n = _next_wave_number()
    assert n >= 707


def test_ignite():
    m = ignite(workers=2, force=False, scaffold=False, captions=True)
    assert m["status"] == "ix_kernel"
    assert m["phases_total"] >= 2


def test_707():
    assert w707.coherence_vitals()["wave"] == 707
