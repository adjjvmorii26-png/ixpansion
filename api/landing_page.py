"""Landing page handler — serves the alexalex.info showcase."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict

HTML_PATH = Path(__file__).resolve().parent.parent / "alexalex-site" / "index.html"

def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    """Return the landing page HTML."""
    try:
        html = HTML_PATH.read_text(encoding="utf-8")
        return {"html": html, "content_type": "text/html"}
    except Exception as e:
        return {"error": str(e), "fallback": "IXPANSION — The Living Organism"}
