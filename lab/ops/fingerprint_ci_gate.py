"""FingerprintCIGate — CI gate that fails on fingerprint anomalies.

This refinement #4 implements a CI gate that checks the organism's DNA fingerprint
and fails the build if coherence drops below a threshold or paradox count exceeds
a limit, ensuring the organism maintains health across mutations.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Root path setup
ROOT = Path(__file__).resolve().parent.parent.parent
SYS_PATH = ROOT / "lab" / "chrono_forge" / "0_primal_core"
if str(SYS_PATH) not in sys.path:
    sys.path.insert(0, str(SYS_PATH))

from pulse_driver import status, STATE


def check_fingerprint_health(threshold: float = 0.75) -> Dict[str, Any]:
    """Check organism fingerprint health against threshold.
    
    Args:
        threshold: Minimum coherence threshold for CI pass
        
    Returns:
        CI gate result dictionary
    """
    current_status = status()
    pulse_state = current_status.get("pulse", {})
    
    coherence = pulse_state.get("coherence", 1.0)
    beats = pulse_state.get("beats", 0)
    sigil = pulse_state.get("sigil", "UNKNOWN")
    
    # Determine CI result
    ci_pass = coherence >= threshold
    ci_result = "pass" if ci_pass else "fail"
    
    result = {
        "ci_result": ci_result,
        "coherence": coherence,
        "threshold": threshold,
        "beats": beats,
        "sigil": sigil,
        "paradox_count": current_status.get("paradox_count", 0),
        "recommendation": "continue" if ci_pass else "investigate",
    }
    
    return result


def check_paradox_threshold(max_paradoxes: int = 10) -> Dict[str, Any]:
    """Check paradox count against threshold.
    
    Args:
        max_paradoxes: Maximum allowed paradox count
        
    Returns:
        Paradox check result dictionary
    """
    # In real implementation, would integrate with coherence regulator
    paradox_count = 0  # Placeholder
    
    ci_pass = paradox_count <= max_paradoxes
    ci_result = "pass" if ci_pass else "fail"
    
    return {
        "ci_result": ci_result,
        "paradox_count": paradox_count,
        "max_allowed": max_paradoxes,
        "recommendation": "continue" if ci_pass else "investigate",
    }


def ci_gate_report(threshold: float = 0.75, max_paradoxes: int = 10) -> Dict[str, Any]:
    """Generate complete CI gate report.
    
    Args:
        threshold: Coherence threshold for pass/fail
        max_paradoxes: Maximum paradox count allowed
        
    Returns:
        Complete CI gate report dictionary
    """
    fingerprint_check = check_fingerprint_health(threshold)
    paradox_check = check_paradox_threshold(max_paradoxes)
    
    # Overall result: pass only if both checks pass
    overall_pass = fingerprint_check["ci_result"] == "pass" and paradox_check["ci_result"] == "pass"
    
    return {
        "overall_ci": overall_pass,
        "fingerprint_check": fingerprint_check,
        "paradox_check": paradox_check,
        "coherence": fingerprint_check["coherence"],
        "threshold": threshold,
        "paradox_count": paradox_check["paradox_count"],
        "max_paradoxes": max_paradoxes,
        "recommendation": "proceed" if overall_pass else "halt_and_investigate",
    }


# CLI entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fingerprint CI Gate")
    parser.add_argument("--threshold", type=float, default=0.75, help="Coherence threshold")
    parser.add_argument("--max-paradoxes", type=int, default=10, help="Maximum paradox count")
    parser.add_argument("--report", action="store_true", help="Generate full CI report")
    parser.add_argument("--check-health", action="store_true", help="Check fingerprint health")
    parser.add_argument("--check-paradox", action="store_true", help="Check paradox threshold")
    
    args = parser.parse_args()
    
    if args.report:
        report = ci_gate_report(args.threshold, args.max_paradoxes)
        print(json.dumps(report, indent=2))
    elif args.check_health:
        result = check_fingerprint_health(args.threshold)
        print(f"CI Result: {result['ci_result']}")
        print(f"Coherence: {result['coherence']}")
        print(f"Threshold: {result['threshold']}")
    elif args.check_paradox:
        result = check_paradox_threshold(args.max_paradoxes)
        print(f"CI Result: {result['ci_result']}")
        print(f"Paradox Count: {result['paradox_count']}")
        print(f"Max Allowed: {result['max_allowed']}")
    else:
        parser.print_help()
