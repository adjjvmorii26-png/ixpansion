import json
import time
from pathlib import Path
from typing import Any


class LogSink:
    """Structured log writer with optional file persistence."""

    def __init__(self, filepath: str | None = None) -> None:
        self._path = Path(filepath) if filepath else None

    def emit(self, level: str, source: str, message: str, **extra: Any) -> None:
        entry = {
            "timestamp": time.time(),
            "level": level,
            "source": source,
            "message": message,
            **extra,
        }
        line = json.dumps(entry)
        print(line)
        if self._path:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "a") as f:
                f.write(line + "\n")
