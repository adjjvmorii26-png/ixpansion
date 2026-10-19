import pytest
from api.cors_middleware import CORSMiddleware

def test_wildcard_origin_configuration_is_rejected():
    with pytest.raises(ValueError, match="Wildcard CORS origins are forbidden"):
        CORSMiddleware(origins=["*"])

def test_allowed_origin_response_varies_by_origin():
    headers = CORSMiddleware().apply("https://ixpansion-live.vercel.app")
    assert headers["Vary"] == "Origin"

def test_preflight_response_varies_by_origin():
    headers = CORSMiddleware().preflight("https://ixpansion-live.vercel.app")
    assert headers["Vary"] == "Origin"
