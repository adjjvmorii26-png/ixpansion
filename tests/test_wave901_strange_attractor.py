from api.wave901_strange_attractor import attract, handler

def test_attractor_is_replayable():
    events=[{"id":"a","fingerprint":"abc"},{"id":"b","fingerprint":"def"}]
    assert attract(events,12)==attract(events,12)

def test_trajectory_length():
    assert len(attract([],7)["trajectory"])==7

def test_status():
    assert handler()["wave"]==901
