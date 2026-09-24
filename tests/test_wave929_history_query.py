from api.wave929_history_query import query

def test_query_filters_changed_history():
    h=[{"sequence":0,"changed":False},{"sequence":1,"changed":True},{"sequence":2,"changed":True}]
    out=query(h,True)
    assert out["sequences"]==[1,2]
    assert out["count"]==2

def test_query_without_filter_preserves_history():
    h=[{"sequence":0,"changed":False}]
    out=query(h)
    assert out["history"]==h
    assert out["interpretation"]=="descriptive_filter_only"
