from api.cors_middleware import allow_origin, DEFAULT_ORIGINS


def test_wildcard_is_never_emitted():
    assert allow_origin("*") == ""
    assert allow_origin(None) == ""
    assert allow_origin("https://evil.example") == ""


def test_production_origin_is_explicit():
    origin = "https://ixpansion-live.vercel.app"
    assert origin in DEFAULT_ORIGINS
    assert allow_origin(origin) == origin


def test_star_in_configured_origins_is_refused():
    assert allow_origin("https://ixpansion-live.vercel.app", origins=["*"]) == ""
