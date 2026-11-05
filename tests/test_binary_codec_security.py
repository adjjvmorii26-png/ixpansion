"""Security regression tests for the Omega Prime binary codec."""
import os
import pickle

import pytest

from omega_prime.nucleus.utilities.exception_map import OmegaPrimeError
from omega_prime.protocols.serialization.binary_codec import dumps, loads


def test_binary_codec_round_trips_primitive_payloads():
    payload = {
        "name": "safe-payload",
        "count": 3,
        "enabled": True,
        "items": [1, 2.5, None, "text"],
    }
    assert loads(dumps(payload)) == payload


def test_binary_codec_rejects_global_callable_reducers(tmp_path):
    marker = tmp_path / "pickle-executed"

    class MaliciousPayload:
        def __reduce__(self):
            return os.system, (f"touch {marker}",)

    encoded = pickle.dumps(MaliciousPayload())
    with pytest.raises(OmegaPrimeError):
        loads(encoded)

    assert not marker.exists()


def test_binary_codec_rejects_non_bytes_input():
    with pytest.raises(OmegaPrimeError):
        loads("not bytes")
