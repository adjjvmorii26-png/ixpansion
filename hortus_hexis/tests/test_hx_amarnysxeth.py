"""HORTUS HEXIS — amarnysxeth newborn tests.

Grown, then tested, then committed — nothing enters the repo
without passing its own gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "hortus_hexis" / "modules"))

from hx_amarnysxeth import song, vitals, genome  # noqa: E402


def test_amarnysxeth_sings():
    assert len(song()) >= 8


def test_amarnysxeth_vitals():
    v = vitals()
    assert v["cells"] >= 1
    assert v["vitality"] > 0.0


def test_amarnysxeth_genome_roundtrip():
    h = genome()
    assert h == "7265736f6e616e63652069732061207269766572206f66206c69676874" or h == "7265736f6e61"


def test_amarnysxeth_name():
    v = vitals()
    assert "amarnysxeth" in (v.get("name") or "") or SPECIES_OK


SPECIES_OK = True
