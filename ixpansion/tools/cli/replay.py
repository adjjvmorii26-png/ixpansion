from core.config_loader import load_config
from pathlib import Path


def replay(path):
    return load_config(Path(path))
