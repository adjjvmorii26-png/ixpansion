from api.cors_middleware import CORSMiddleware

def test_default_cors_does_not_allow_wildcard():
    middleware = CORSMiddleware()
    assert "*" not in middleware.origins

def test_untrusted_origin_is_not_reflected():
    middleware = CORSMiddleware()
    headers = middleware.apply("https://evil.example")
    assert headers["Access-Control-Allow-Origin"] == ""

def test_configured_production_origin_is_allowed():
    middleware = CORSMiddleware()
    assert middleware.apply("https://ixpansion-live.vercel.app")["Access-Control-Allow-Origin"] == "https://ixpansion-live.vercel.app"

def test_preflight_rejects_untrusted_origin():
    middleware = CORSMiddleware()
    assert middleware.preflight("https://evil.example")["Access-Control-Allow-Origin"] == ""
