"""Wave 952 caretaker_quorum tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave952_caretaker_quorum as w


def test_superseded_closes():
    out = w.decide({"title": "lab: old", "head": "lab/old", "superseded": True})
    assert out["action"] == "close"
    assert out["reason"] == "superseded_or_conflicted"
    assert out["audio"] is None
    assert out["surface"] == "silence"


def test_dirty_closes():
    out = w.decide({"title": "lab: cors", "head": "lab/wave951", "mergeable_state": "dirty"})
    assert out["action"] == "close"


def test_lab_green_merges():
    out = w.decide(
        {
            "title": "lab: wave952",
            "head": "lab/wave952-caretaker-quorum",
            "lab_gate": "pass",
            "organism_gate": "unknown",
            "mergeable_state": "clean",
        }
    )
    assert out["track"] == "lab"
    assert out["action"] == "merge"
    assert out["reason"] == "lab_green_safe"


def test_organism_red_holds():
    out = w.decide(
        {
            "title": "security: auth",
            "head": "security/auth",
            "organism_gate": "fail",
            "mergeable_state": "behind",
        }
    )
    assert out["track"] == "security"
    assert out["action"] == "hold"
    assert out["reason"] == "gate_red"


def test_handler_and_vitals():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    assert w.handler()["wave"] == 952
    assert w.handler()["audio"] is False
    decided = w.handler({"action": "decide", "title": "lab: x", "head": "lab/x", "lab_gate": "pass"})
    assert decided["status"] == "decided"
    assert decided["action"] == "merge"
    q = w.handler(
        {
            "action": "quorum",
            "pulls": [
                {"title": "lab: a", "head": "lab/a", "lab_gate": "pass"},
                {"title": "security: b", "head": "security/b", "organism_gate": "fail"},
            ],
        }
    )
    assert q["status"] == "quorum"
    assert q["counts"]["merge"] >= 1
    assert q["counts"]["hold"] >= 1
    v = w.coherence_vitals()
    assert v["wave"] == 952
    assert v["ok"] is True
    assert "wave787_dual_track_pr_bot" in w.resonates_with()
    assert "wave950_hush_margin" in w.resonates_with()
