from api.wave900_synchronicity_engine import field, handler

def test_field_is_replayable():
    events=[{"id":"a","title":"dream garden","text":"new patterns emerge"},{"id":"b","title":"garden patterns","text":"new patterns return"}]
    assert field(events)==field(events)

def test_field_detects_shared_tokens():
    result=field([{"id":"a","title":"dream garden","text":"patterns emerge"},{"id":"b","title":"garden patterns","text":"patterns return"}])
    assert result["collisions"]
    assert result["collisions"][0]["affinity"]>0

def test_status():
    assert handler()["wave"]==900
