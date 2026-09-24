from api.wave930_history_window import window

def test_window_is_sequence_ordered():
    h=[{"sequence":2},{"sequence":0},{"sequence":1}]
    out=window(h,1,2)
    assert out["sequences"]==[1,2]
    assert out["count"]==2

def test_window_without_limit_returns_tail():
    h=[{"sequence":0},{"sequence":1},{"sequence":2}]
    out=window(h,2)
    assert out["sequences"]==[2]

def test_window_is_descriptive_only():
    out=window([{"sequence":0}],0,1)
    assert out["interpretation"]=="descriptive_window_only"
    assert "winner" not in out
