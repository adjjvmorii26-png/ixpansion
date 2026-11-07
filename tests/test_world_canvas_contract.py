from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "lab" / "world-canvas" / "index.html"
ENGINE = ROOT / "lab" / "world-canvas" / "world-engine.mjs"
NODE_TESTS = ROOT / "lab" / "world-canvas" / "world-engine.test.mjs"
SKILL = ROOT / "skills" / "r1" / "world_canvas_gem" / "SKILL.md"


def test_world_canvas_artifacts_exist():
    assert all(path.is_file() for path in (PAGE, ENGINE, NODE_TESTS, SKILL))


def test_interface_uses_separate_pure_engine():
    html = PAGE.read_text(encoding="utf-8")
    engine = ENGINE.read_text(encoding="utf-8")
    assert 'from "./world-engine.mjs"' in html
    assert "function draw()" in html
    assert "export function transition(" in engine
    assert "export function hashWorld(" in engine
    assert "export function validateWorld(" in engine


def test_rendering_is_read_only_and_accessible():
    html = PAGE.read_text(encoding="utf-8")
    draw = html.split("function draw(){", 1)[1].split("function render(){", 1)[0]
    assert "world.beacons" in draw
    assert "pulseTicks--" not in draw
    assert "prefers-reduced-motion:reduce" in html
    assert 'role="status"' in html
    assert 'aria-label="World map.' in html


def test_gem_harness_has_approval_and_evidence_contracts():
    skill = SKILL.read_text(encoding="utf-8")
    for phrase in ("Plan before mutation", "Determinism", "Pure transitions", "Evidence", "Approval gate", "No false physics"):
        assert phrase in skill
    assert "world-canvas:replay" in skill
    assert "world-canvas:package" in skill
