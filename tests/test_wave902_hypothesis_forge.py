from api.wave902_hypothesis_forge import forge, handler

def test_forge_is_replayable():
    e=[{"id":"a","fingerprint":"one"},{"id":"b","fingerprint":"two"}]
    t=[{"x":.1,"y":.2,"z":.3}]*6
    assert forge(e,t)==forge(e,t)

def test_proposals_are_not_executable():
    r=forge([],[],4)
    assert r["executable"] is False
    assert len(r["proposals"])==4

def test_status():
    assert handler()["wave"]==902
