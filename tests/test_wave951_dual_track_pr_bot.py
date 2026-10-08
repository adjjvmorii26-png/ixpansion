from api.wave951_dual_track_pr_bot import classify, handler, coherence_vitals, resonates_with


def test_experiment_branch_stays_on_lab_gate():
    out = classify({"title": "experiment: REAL-035", "head": "experiment/real-035", "files": ["api/wave923_ledger_reconciliation.py"]})
    assert out["track"] == "lab"
    assert out["merge_gate"] == "lab"
    assert out["do_not_merge"] is True
    assert out["audio"] is None


def test_lab_touching_runtime_is_dual():
    out = classify({"title": "lab: cors", "head": "lab/cors", "files": ["api_server.py"]})
    assert out["track"] == "dual"
    assert out["merge_gate"] == "organism"


def test_handler_and_vitals():
    assert handler()["wave"] == 951
    assert handler()["audio"] is None
    assert "error" in handler({"action": "sing"})
    assert coherence_vitals()["wave"] == "951"
    assert "wave950_hush_margin" in resonates_with()
