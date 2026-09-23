from api.wave903_experiment_chamber import chamber, handler

def test_simulation_is_replayable():
    e=[{"id":"a"},{"id":"b"}]; r=[{"op":"remove","index":1},{"op":"add","event":{"id":"c"}}]
    assert chamber(e,r)==chamber(e,r)

def test_unknown_operation_rejected():
    out=chamber([{"id":"a"}],[{"op":"execute_code","code":"x"}])
    assert out["results"][0]["status"]=="rejected"

def test_no_external_actions():
    assert chamber([],[])["executed_external_actions"] is False
    assert handler()["wave"]==903
