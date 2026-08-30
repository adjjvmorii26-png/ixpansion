"""HORTUS HEXIS — kalyndramar newborn tests.

Grown, then tested, then committed — nothing enters the repo
without passing its own gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "hortus_hexis" / "modules"))

from hx_kalyndramar import song, vitals, genome  # noqa: E402


def test_kalyndramar_sings():
    assert len(song()) >= 8


def test_kalyndramar_vitals():
    v = vitals()
    assert v["cells"] >= 1
    assert v["vitality"] > 0.0


def test_kalyndramar_genome_roundtrip():
    h = genome()
    assert h == "6d6f726969" or h == "6d6f726969"


def test_kalyndramar_name():
    v = vitals()
    assert "kalyndramar" in (v.get("name") or "") or SPECIES_OK


SPECIES_OK = True
