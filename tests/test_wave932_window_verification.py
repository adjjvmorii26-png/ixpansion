from api.wave931_window_integrity import attest
from api.wave932_window_verification import verify

def test_matching_attestation_verifies():
    w={"start":0,"limit":2,"sequences":[0,1],"history":[{"sequence":0},{"sequence":1}]}
    a=attest(w)
    out=verify(w,a)
    assert out["match"] is True

def test_mutation_fails_verification():
    w={"start":0,"limit":1,"sequences":[0],"history":[{"sequence":0}]}
    a=attest(w)
    mutated={"start":0,"limit":1,"sequences":[0],"history":[{"sequence":9}]}
    assert verify(mutated,a)["match"] is False

def test_verification_is_integrity_only():
    out=verify({"history":[]},{"fingerprint":"x"})
    assert out["interpretation"]=="integrity_verification_only"
    assert "correct" not in out
