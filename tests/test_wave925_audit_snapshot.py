from api.wave925_audit_snapshot import snapshot

def test_snapshot_is_deterministic():
    audit={"status":"delta_present","counts":{"added":1,"removed":0,"changed":1},
           "sequences":{"added":["2"],"removed":[],"changed":["1"]}}
    assert snapshot(audit)==snapshot(audit)

def test_snapshot_normalizes_sequence_order():
    a={"counts":{"added":2},"sequences":{"added":["2","1"]}}
    b={"counts":{"added":2},"sequences":{"added":["1","2"]}}
    assert snapshot(a)["fingerprint"]==snapshot(b)["fingerprint"]

def test_snapshot_is_state_capture_only():
    out=snapshot({"status":"no_delta","counts":{},"sequences":{}})
    assert out["interpretation"]=="state_capture_only"
    assert "confidence" not in out
