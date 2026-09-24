from api.wave927_diff_summary import summarize

def test_summary_is_deterministic():
    out=summarize({"changed_fields":["status","counts"]})
    assert out["changed"] is True
    assert out["changed_fields"]==["counts","status"]
    assert out["change_count"]==2

def test_empty_diff_is_clean():
    out=summarize({"changed_fields":[]})
    assert out["changed"] is False
    assert out["change_count"]==0

def test_summary_is_descriptive_only():
    out=summarize({"changed_fields":["status"]})
    assert out["interpretation"]=="descriptive_diff_summary_only"
    assert "winner" not in out
