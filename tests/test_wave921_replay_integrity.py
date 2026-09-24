from api.wave921_replay_integrity import fingerprint, attest

def test_fingerprint_is_deterministic():
    trace={"wave":920,"steps":[{"step":"normalize_tokens","tokens":["a"]}]}
    assert fingerprint(trace)==fingerprint({"steps":trace["steps"],"wave":920})

def test_fingerprint_changes_when_trace_changes():
    a={"wave":920,"steps":[{"step":"normalize_tokens","tokens":["a"]}]}
    b={"wave":920,"steps":[{"step":"normalize_tokens","tokens":["b"]}]}
    assert fingerprint(a)!=fingerprint(b)

def test_attestation_is_integrity_only():
    out=attest({"wave":920,"steps":[]})
    assert out["integrity_only"] is True
    assert out["interpretation"]=="mutation_detection_only"
