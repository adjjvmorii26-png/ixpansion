from api.wave921_replay_integrity import fingerprint, attest

def test_replay_fingerprint_has_full_contract_width():
    trace={"wave":920,"steps":[{"step":"normalize_tokens","tokens":["alpha"]}]}
    fp=fingerprint(trace)
    assert len(fp)==16
    assert len(attest(trace)["fingerprint"])==16
    assert all(c in "0123456789abcdef" for c in fp)
