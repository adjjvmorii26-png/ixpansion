"""Lab OS Boot + subprocess vitals."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "lab" / "ops"))
sys.path.insert(0, str(ROOT / "api"))

from subprocess_vitals import vitals_isolated
from lab_os_boot import boot
import wave706_lab_os_boot as w706


def test_subprocess_vitals_on_self():
    path = ROOT / "api" / "wave705_lab_jumpstart.py"
    if not path.exists():
        path = ROOT / "api" / "wave704_lab_epoch_seal.py"
    if path.exists():
        v = vitals_isolated(path, timeout=20)
        assert isinstance(v, dict)
        assert "module" in v or "ok" in v


def test_lab_os_boot():
    m = boot(force=False, workers=2, still_seconds=0.5)
    assert m["status"] == "lab_os_boot"
    assert m["layers_total"] >= 3


def test_706():
    assert w706.coherence_vitals()["wave"] == 706
