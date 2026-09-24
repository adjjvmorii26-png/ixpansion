from api.wave923_ledger_reconciliation import reconcile

def test_reconciliation_reports_structural_differences():
    before={"entries":[{"sequence":0,"fingerprint":"a","source":"x"},{"sequence":1,"fingerprint":"b","source":"x"}]}
    after={"entries":[{"sequence":0,"fingerprint":"a","source":"x"},{"sequence":1,"fingerprint":"c","source":"x"},{"sequence":2,"fingerprint":"d","source":"y"}]}
    out=reconcile(before,after)
    assert out["added_sequences"]==["2"]
    assert out["removed_sequences"]==[]
    assert out["changed_sequences"]==["1"]

def test_identical_ledgers_have_no_differences():
    x={"entries":[{"sequence":0,"fingerprint":"a","source":"x"}]}
    out=reconcile(x,x)
    assert out["counts"]=={"added":0,"removed":0,"changed":0}
    assert out["interpretation"]=="structural_reconciliation_only"

def test_removals_are_reported():
    out=reconcile({"entries":[{"sequence":0},{"sequence":1}]},{"entries":[{"sequence":0}]})
    assert out["removed_sequences"]==["1"]
