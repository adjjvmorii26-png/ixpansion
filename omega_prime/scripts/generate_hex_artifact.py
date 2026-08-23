"""Generate and save a binary hex artifact."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from omega_prime.protocols.hex.encoder import frame


def main() -> None:
    payload = {
        "artifact": "genesis",
        "version": 1,
        "agents": ["scout-01", "guard-01"],
        "realm": "lattice",
    }
    raw = frame(payload, dialect=2)
    out = Path(__file__).parent.parent / "data" / "genesis.op"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(raw)
    print(f"artifact saved: {out} ({len(raw)} bytes)")


if __name__ == "__main__":
    main()
