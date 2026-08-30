"""HORTUS HEXIS — cross-pollination + web API tests (no network, no git)."""
from __future__ import annotations

import json
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hortus_hexis.cross import hybrid_seed, hybrid_name  # noqa: E402
from hortus_hexis.growth import Organism  # noqa: E402
from hortus_hexis.seed import words_to_seed  # noqa: E402

A_SEED = words_to_seed("morii")
B_SEED = words_to_seed("let the garden remember")
A_NAME = "kalyndramar"
B_NAME = "syphexnysorev"


def test_hybrid_seed_deterministic():
    h1 = hybrid_seed(A_SEED, B_SEED)
    h2 = hybrid_seed(A_SEED, B_SEED)
    assert h1 == h2
    assert h1 != A_SEED and h1 != B_SEED


def test_hybrid_seed_unique_per_pair():
    # parent order affects the fusion salt (ordered cross), so reversed differs.
    assert hybrid_seed(A_SEED, B_SEED) != hybrid_seed(B_SEED, A_SEED)
    assert hybrid_seed(A_SEED, A_SEED) == hybrid_seed(A_SEED, A_SEED)


def test_hybrid_name_splices():
    n = hybrid_name(A_NAME, B_NAME)
    assert len(n) >= 4
    assert n.startswith(A_NAME[:3]) or n.startswith(A_NAME[:5])
    assert n.endswith(B_NAME[-3:]) or n in (A_NAME, B_NAME)


def test_hybrid_grows_organism():
    seed = hybrid_seed(A_SEED, B_SEED)
    o = Organism(hybrid_name(A_NAME, B_NAME), seed, "hybrid test")
    assert len(o.cells) >= 1 and o.vitality > 0


def test_web_organisms_payload():
    from hortus_hexis.web import _organisms_payload
    d = _organisms_payload()
    assert "count" in d and "organisms" in d
    assert isinstance(d["organisms"], list)


def test_web_plant_gate_no_commit():
    """Planting must at least gate (no git commit; if gate fails, error)."""
    from hortus_hexis.web import _plant
    probe_words = "web gate probe — zulu yankee xray"
    r = _plant(probe_words, commit=False)
    assert "error" not in r or r.get("error") != "gate closed"
    assert "name" in r
    name = r["name"]
    # clean up every artifact the gate created (module, test, specimen + registry)
    for f in (ROOT / "hortus_hexis" / "modules").glob(f"hx_{name}.py"):
        f.unlink(missing_ok=True)
    for f in (ROOT / "hortus_hexis" / "tests").glob(f"test_hx_{name}.py"):
        f.unlink(missing_ok=True)
    spec = ROOT / "hortus_hexis" / "organisms" / f"{name}.json"
    spec.unlink(missing_ok=True)
    reg = ROOT / "hortus_hexis" / "registry.json"
    import json
    if reg.exists():
        try:
            rows = json.loads(reg.read_text())
            rows = [e for e in rows if e.get("name") != name]
            reg.write_text(json.dumps(rows, indent=2))
        except Exception:
            pass


def test_web_cross_gate_no_commit():
    from hortus_hexis.web import _cross
    r = _cross(A_NAME, B_NAME, commit=False)
    assert "name" in r
    assert r.get("parents") == [A_NAME, B_NAME]
