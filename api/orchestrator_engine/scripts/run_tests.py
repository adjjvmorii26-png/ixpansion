#!/usr/bin/env python3
"""Run the organism orchestrator test suite."""

import sys
sys.path.insert(0, '.')

from tests.test_basic import test_init, test_module_lifecycle, test_wave_evolution, test_persona_evolution

if __name__ == "__main__":
    test_init()
    test_module_lifecycle()
    test_wave_evolution()
    test_persona_evolution()
    print("
✓ All tests passed!")
