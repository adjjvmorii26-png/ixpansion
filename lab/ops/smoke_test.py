"""Lab Smoke Test — verifies the organism's lab subystems are alive."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab"))

def test_chronoweave_portal():
    from chronoweave.cw_portal import boot
    result = boot()
    assert isinstance(result, dict), "Chronoweave boot should return dict"
    print("✓ Chronoweave portal alive")

def test_paradox_forge_portal():
    from paradox_forge.pf_portal import boot
    result = boot()
    assert isinstance(result, dict), "Paradox Forge boot should return dict"
    print("✓ Paradox Forge portal alive")

def test_polygenesis_portal():
    from polygenesis.pg_portal import boot
    result = boot()
    assert isinstance(result, dict), "Polygenesis boot should return dict"
    print("✓ Polygenesis portal alive")

def test_chronoforge_portal():
    from CHRONOFORGE.runtime.cf_portal import boot
    result = boot()
    assert isinstance(result, dict), "ChronoForge boot should return dict"
    print("✓ ChronoForge portal alive")

def test_stratum_portal():
    from STRATUM_ENGINE.runtime.se_portal import boot
    result = boot()
    assert isinstance(result, dict), "Stratum Engine boot should return dict"
    print("✓ Stratum Engine portal alive")

def test_monolith_portal():
    from MONOLITH_STACK.runtime.ms_portal import boot
    result = boot()
    assert isinstance(result, dict), "Monolith Stack boot should return dict"
    print("✓ Monolith Stack portal alive")

def test_run_pinned():
    from lab.run_pinned import build_parser
    parser = build_parser()
    assert parser is not None
    print("✓ Lab run_pinned accessible")

if __name__ == "__main__":
    test_chronoweave_portal()
    test_paradox_forge_portal()
    test_polygenesis_portal()
    test_chronoforge_portal()
    test_stratum_portal()
    test_monolith_portal()
    test_run_pinned()
    print("\n✓ ALL LAB PORTALS ALIVE")
