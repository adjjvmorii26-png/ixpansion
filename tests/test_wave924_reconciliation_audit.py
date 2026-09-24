from api.wave924_reconciliation_audit import audit

def test_audit_counts_differences():
    out=audit({"added_sequences":["2"],"removed_sequences":[],"changed_sequences":["1"],
               "counts":{"added":1,"removed":0,"changed":1}})
    assert out["status"]=="delta_present"
    assert out["total_differences"]==2

def test_empty_reconciliation_is_no_delta():
    out=audit({"counts":{"added":0,"removed":0,"changed":0}})
    assert out["status"]=="no_delta"
    assert out["total_differences"]==0

def test_audit_is_structural_only():
    out=audit({"counts":{"added":1,"removed":0,"changed":0},"added_sequences":["1"]})
    assert out["interpretation"]=="structural_audit_only"
    assert "confidence" not in out
