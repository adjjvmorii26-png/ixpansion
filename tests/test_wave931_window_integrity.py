from api.wave931_window_integrity import attest

def test_attestation_is_deterministic():
    w={"start":0,"limit":2,"sequences":[0,1],"history":[{"sequence":0},{"sequence":1}]}
    assert attest(w)["fingerprint"]==attest(w)["fingerprint"]

def test_attestation_changes_with_window_state():
    a={"start":0,"limit":1,"sequences":[0],"history":[{"sequence":0}]}
    b={"start":0,"limit":1,"sequences":[0],"history":[{"sequence":1}]}
    assert attest(a)["fingerprint"]!=attest(b)["fingerprint"]

def test_integrity_has_no_truth_claim():
    out=attest({"history":[]})
    assert out["interpretation"]=="window_integrity_only"
    assert "confidence" not in out
