import re
from pathlib import Path

def test_api_server_has_no_wildcard_cors():
    source = Path("api_server.py").read_text(encoding="utf-8")
    assert not re.search(r'Access-Control-Allow-Origin",\s*"\\*"', source)
    assert source.count("_write_cors_headers()") >= 2
