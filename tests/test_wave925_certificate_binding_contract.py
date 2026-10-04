import hashlib
import json

from api.wave925_audit_snapshot import snapshot

def test_audit_certificate_is_bound_to_entire_snapshot():
    a={"status":"delta_present","counts":{"added":1},"sequences":{"added":["a"]}}
    b={"status":"delta_present","counts":{"added":2},"sequences":{"added":["a"]}}
    out=snapshot(a)
    expected=hashlib.sha256(
        json.dumps(out["snapshot"],sort_keys=True,separators=(",",":"),default=str).encode()
    ).hexdigest()[:16]
    assert out["fingerprint"]==expected
    assert out["fingerprint"]!=snapshot(b)["fingerprint"]
