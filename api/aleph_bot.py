from __future__ import annotations
"""Aleph Bot — restored assembler (env-only TELEGRAM_BOT_TOKEN)."""
import base64, pathlib
_HERE = pathlib.Path(__file__).resolve().parent
_parts = sorted(_HERE.glob("_aleph_part_*.txt"))
if not _parts:
    raise RuntimeError("aleph_bot parts missing — incomplete security restore")
_src = base64.b64decode("".join(p.read_text() for p in _parts).encode()).decode()
_ns = {"__name__": __name__, "__file__": __file__}
exec(compile(_src, str(_HERE / "_aleph_bot_restored.py"), "exec"), _ns)
globals().update({k: v for k, v in _ns.items() if not k.startswith("_")})
