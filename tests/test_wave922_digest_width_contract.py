from api.wave922_integrity_ledger import append

def test_ledger_digest_has_full_contract_width():
    out=append([],{"fingerprint":"abc","source":"exp-1"})
    digest=out["ledger_digest"]
    assert len(digest)==16
    assert all(c in "0123456789abcdef" for c in digest)
