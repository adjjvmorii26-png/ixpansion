"""Wave 806 registry tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))

import wave806_organ_registry as w806


def test_inspect_file_is_static(tmp_path):
    p = tmp_path / "organ.py"
    p.write_text(
        "import json\n"
        "def handler(req=None): return {}\n"
        "def coherence_vitals(): return {}\n"
        "def resonates_with(): return []\n"
        "STATE_FILE = 'data/x.json'\n"
    )
    result = w806.inspect_file(p)
    assert result["valid"] is True
    assert result["contract"] == {
        "handler": True,
        "coherence_vitals": True,
        "resonates_with": True,
    }
    assert result["stateful"] is True
    assert "json" in result["imports"]


def test_registry_counts_contract_gaps(tmp_path):
    (tmp_path / "good.py").write_text(
        "def handler(req=None): pass\n"
        "def coherence_vitals(): pass\n"
        "def resonates_with(): return []\n"
    )
    (tmp_path / "gap.py").write_text("def handler(req=None): pass\n")
    (tmp_path / "broken.py").write_text("def nope(:\n")
    result = w806.registry(tmp_path)
    assert result["total"] == 3
    assert result["valid"] == 2
    assert result["invalid"] == 1
    assert result["contract_complete"] == 1
    assert result["contract_gap"] == 1


def test_status_does_not_import_organs():
    result = w806.handler({"action": "status"})
    assert result["wave"] == 806
    assert result["surface"] == "registry"
    assert "contract_gap" in result
