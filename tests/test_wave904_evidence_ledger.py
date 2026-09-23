from api.wave904_evidence_ledger import record, ledger, handler

def test_record_is_deterministic():
    a=record({"id":"H"},{"op":"add"},[1],[1,2],"x")
    b=record({"id":"H"},{"op":"add"},[1],[1,2],"x")
    assert a==b

def test_duplicate_records_are_collapsed():
    r=record({"id":"H"},{"op":"add"},[],[1])
    out=ledger([r,r])
    assert out["count"]==1

def test_status():
    assert handler()["wave"]==904
