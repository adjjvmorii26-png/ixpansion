from api.wave926_snapshot_diff import diff

def test_diff_reports_changed_fields():
    a={"snapshot":{"status":"no_delta","counts":{"added":0},"sequences":{}}}
    b={"snapshot":{"status":"delta_present","counts":{"added":1},"sequences":{"added":["1"]}}}
    out=diff(a,b)
    assert out["changed_fields"]==["counts","sequences","status"]
    assert out["change_count"]==3

def test_identical_snapshots_have_no_changes():
    x={"snapshot":{"status":"no_delta","counts":{},"sequences":{}}}
    out=diff(x,x)
    assert out["changed_fields"]==[]
    assert out["change_count"]==0

def test_diff_is_not_a_correctness_judgment():
    out=diff({"snapshot":{"status":"a"}},{"snapshot":{"status":"b"}})
    assert out["interpretation"]=="state_diff_only"
    assert "winner" not in out
