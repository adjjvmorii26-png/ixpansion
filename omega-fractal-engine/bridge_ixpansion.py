#!/usr/bin/env python3
"""Compatibility launcher for the underscore-named Omega Fractal Engine."""
import runpy
from pathlib import Path

target = Path(__file__).resolve().parents[1] / "omega_fractal_engine" / "bridge_ixpansion.py"
runpy.run_path(str(target), run_name="__main__")
