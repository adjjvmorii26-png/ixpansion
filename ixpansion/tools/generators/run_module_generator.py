from pathlib import Path
from tools.generators.module_gen import generate


if __name__ == "__main__":
    print(generate("generated_module", Path("generated_module.py")))
