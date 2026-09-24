from api.wave928_diff_history import append

def test_history_is_ordered():
    a=append([],{"changed":False})
    b=append(a["history"],{"changed":True})
    assert [x["sequence"] for x in b["history"]]==[0,1]
    assert b["count"]==2

def test_history_is_descriptive_only():
    out=append([],{"changed":True})
    assert out["interpretation"]=="descriptive_history_only"
    assert "winner" not in out
