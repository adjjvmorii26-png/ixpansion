import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "fast: marks tests as fast (wave tests)")
