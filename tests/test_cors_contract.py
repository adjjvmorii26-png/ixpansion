from api.cors_middleware import CORSMiddleware

def test_default_cors_is_not_wildcard():
    middleware = CORSMiddleware()
    assert "*" not in middleware.origins

def test_untrusted_origin_is_rejected():
    middleware = CORSMiddleware()
    assert middleware.apply("https://evil.example")["Access-Control-Allow-Origin"] == ""

def test_production_origin_is_allowed():
    middleware = CORSMiddleware()
    assert middleware.apply("https://ixpansion-live.vercel.app")["Access-Control-Allow-Origin"] == "https://ixpansion-live.vercel.app"
