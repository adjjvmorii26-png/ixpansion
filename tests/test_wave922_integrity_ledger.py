import pytest
from api.wave922_integrity_ledger import append, verify

def test_append_requires_provenance_and_fingerprint():
    with pytest.raises(ValueError, match="fingerprint"):
        append([],{"source":"exp"})
    with pytest.raises(ValueError, match="source"):
        append([],{ "fingerprint":"abc"})

def test_append_is_ordered():
    out=append([],{"fingerprint":"abc","source":"exp-1"})
    assert out["entries"][0]["sequence"]==0
    out2=append(out["entries"],{"fingerprint":"def","source":"exp-2"})
    assert [x["sequence"] for x in out2["entries"]]==[0,1]

def test_verify_detects_sequence_shape():
    out=verify({"entries":[{"sequence":0},{"sequence":1}]})
    assert out["contiguous"] is True
    assert out["entry_count"]==2
