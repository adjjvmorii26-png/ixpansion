from api.wave912_evolution_event_ledger import build

def test_ledger_is_deterministic():
    changes=[{"id":"e2","path":"b.py","kind":"added","evidence_ids":["z"]},{"id":"e1","path":"a.py","kind":"modified"}]
    assert build(changes)["fingerprint"]==build(changes)["fingerprint"]

def test_events_are_sorted_by_id():
    changes=[{"id":"e2","path":"b.py"},{"id":"e1","path":"a.py"}]
    out=build(changes)
    assert [event["id"] for event in out["events"]]==["e1","e2"]

def test_preserves_only_known_evidence_links():
    out=build([{"id":"e1","path":"a.py","evidence_ids":["known","missing"]}],[{"id":"known"}])
    assert out["events"][0]["evidence_ids"]==["known"]
    assert out["summary"]["with_evidence"]==1

def test_unexplained_is_not_regression():
    out=build([{"path":"a.py","classification":"unexplained"}])
    assert out["policy"]["unexplained_is_not_regression"]

def test_change_kind_is_preserved_across_ledger_boundary():
    out=build([
        {"id":"e1","path":"a.py","kind":"modified"},
        {"id":"e2","path":"b.py","kind":"added"},
    ])
    assert [(event["id"],event["kind"]) for event in out["events"]]==[
        ("e1","modified"),("e2","added")
    ]
