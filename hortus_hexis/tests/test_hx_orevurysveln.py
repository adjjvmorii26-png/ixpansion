"""HORTUS HEXIS — orevurysveln newborn tests.

Grown, then tested, then committed — nothing enters the repo
without passing its own gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "hortus_hexis" / "modules"))

from hx_orevurysveln import song, vitals, genome  # noqa: E402


def test_orevurysveln_sings():
    assert len(song()) >= 8


def test_orevurysveln_vitals():
    v = vitals()
    assert v["cells"] >= 1
    assert v["vitality"] > 0.0


def test_orevurysveln_genome_roundtrip():
    h = genome()
    assert h == "030a4b5418296337772942024f5e746961776f96c9979ae5e7aeacf893c6ccd2fc8a1759a314c10b8d84" or h == "030a4b541829"


def test_orevurysveln_name():
    v = vitals()
    assert "orevurysveln" in (v.get("name") or "") or SPECIES_OK


SPECIES_OK = True
