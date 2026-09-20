"""Wave 776 lab tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave776_merge_readiness_score as w776


def test_vitals_contract():
    w776.DATA.mkdir(parents=True, exist_ok=True)
    w776.STATE_FILE.write_text(
        '{"wave":776,"name":"merge_readiness_score","scores":0,"status":"test"}'
    )
    v = w776.coherence_vitals()
    assert v["wave"] == 776
    assert v["policy"] == "organism_gates_gt_ghas_noise"
    assert v["ok"] is True
    assert "helix" in " ".join(w776.resonates_with()) or any(
        "helix" in x or "773" in x for x in w776.resonates_with()
    )


def test_score_organism_over_ghas():
    w776.DATA.mkdir(parents=True, exist_ok=True)
    w776.STATE_FILE.write_text(
        '{"wave":776,"name":"merge_readiness_score","scores":0,"status":"test"}'
    )
    noisy_but_lab_green = w776.handler(
        {
            "action": "score",
            "ref": "pr-lab",
            "signals": {
                "lab_smoke": 1.0,
                "lab_graft": 1.0,
                "lab_gate": 1.0,
                "tests_green": 1.0,
                "ghas_alerts": 0.9,
                "aleph_full_ci": 0.0,
            },
        }
    )
    assert noisy_but_lab_green["audio"] is False
    assert noisy_but_lab_green["verdict"] == "mergeable"
    assert noisy_but_lab_green["score"] >= 0.72

    lab_red = w776.handler(
        {
            "action": "score",
            "signals": {
                "lab_smoke": 0.0,
                "lab_graft": 1.0,
                "lab_gate": 1.0,
                "tests_green": 1.0,
                "ghas_alerts": 0.0,
                "aleph_full_ci": 1.0,
            },
        }
    )
    assert lab_red["verdict"] == "blocked_lab"
    assert lab_red["score"] == 0.0


def test_caption_silent():
    c = w776.handler({"action": "caption"})
    assert c["audio"] is False
    assert c["surface"] == "silence"
    assert "caption" in c
