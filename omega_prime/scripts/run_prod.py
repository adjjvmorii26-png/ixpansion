"""Production entry point with config overlay."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from omega_prime.nucleus.utilities.config_matrix import resolve


def main() -> None:
    base = Path(__file__).parent.parent / "data" / "config_base.json"
    if base.exists():
        cfg = resolve(base)
        print(f"loaded production config: {cfg}")
    else:
        print("no production config found, using defaults")


if __name__ == "__main__":
    main()
