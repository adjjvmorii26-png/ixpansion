from __future__ import annotations

import unittest
from unittest.mock import patch

from integrations.workspace_sync.providers import ProviderProtocolError, _stdlib_transport


class FakeResponse:
    status = 200
    def __init__(self, body: bytes): self.body = body
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, limit: int) -> bytes: return self.body


class ProviderProtocolGuardTests(unittest.TestCase):
    def _assert_rejected(self, body: bytes, message: str):
        response = FakeResponse(body)
        with patch('integrations.workspace_sync.providers.urllib.request.urlopen', return_value=response):
            with self.assertRaisesRegex(ProviderProtocolError, message):
                _stdlib_transport('GET', 'https://provider.invalid', {}, None, 2.0)

    def test_malformed_json_is_a_permanent_protocol_error(self):
        self._assert_rejected(b'{"results":', 'invalid JSON')

    def test_invalid_utf8_is_a_permanent_protocol_error(self):
        self._assert_rejected(bytes([255, 254]), 'invalid JSON')

    def test_oversized_provider_response_is_rejected(self):
        self._assert_rejected(b'x' * 2_000_001, '2 MB limit')

    def test_json_array_is_rejected_when_object_is_required(self):
        self._assert_rejected(b'[]', 'non-object')


if __name__ == '__main__':
    unittest.main()
