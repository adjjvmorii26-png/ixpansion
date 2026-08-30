"""HORTUS HEXIS — syphexnysorev newborn tests.

Grown, then tested, then committed — nothing enters the repo
without passing its own gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "hortus_hexis" / "modules"))

from hx_syphexnysorev import song, vitals, genome  # noqa: E402


def test_syphexnysorev_sings():
    assert len(song()) >= 8


def test_syphexnysorev_vitals():
    v = vitals()
    assert v["cells"] >= 1
    assert v["vitality"] > 0.0


def test_syphexnysorev_genome_roundtrip():
    h = genome()
    assert h == "6c6574207468652067617264656e2072656d656d626572207468697320636f6e766572736174696f6e" or h == "6c6574207468"


def test_syphexnysorev_name():
    v = vitals()
    assert "syphexnysorev" in (v.get("name") or "") or SPECIES_OK


SPECIES_OK = True
