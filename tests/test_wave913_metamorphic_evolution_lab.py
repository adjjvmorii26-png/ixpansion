from api.wave913_metamorphic_evolution_lab import run

def test_reorder_preserves_file_set():
    s=[{"path":"a.py","size":1},{"path":"b.py","size":2}]
    out=run(s,["reorder"],["file_set_preserved"])
    assert out["events"][0]["checks"][0]["outcome"]=="preserved"

def test_unknown_invariant_is_explicit():
    out=run([{"path":"a.py"}],["identity"],["future_invariant"])
    assert out["events"][0]["checks"][0]["outcome"]=="unknown"

def test_deterministic():
    s=[{"path":"b.py"},{"path":"a.py"}]
    assert run(s,["reorder"])["fingerprint"]==run(s,["reorder"])["fingerprint"]
