from __future__ import annotations
"""Cargo Cult Detector — finds code that looks functional but isn't.

Like cargo cult airplanes (wooden replicas that look like planes but
can't fly), some code has the appearance of functionality without
actual purpose. This detector finds dead code, placebo functions,
and decorative patterns that serve no real purpose.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class CargoCultFinding:
    name: str
    finding_type: str
    severity: float
    description: str
    evidence: List[str] = field(default_factory=list)

class CargoCultDetector:
    def __init__(self):
        self.findings: List[CargoCultFinding] = []
        self.scanned_modules: Dict[str, Dict] = {}

    def scan_module(self, name: str, functions: List[Dict]) -> List[CargoCultFinding]:
        module_findings = []
        self.scanned_modules[name] = {"functions": len(functions)}

        for func in functions:
            func_name = func.get("name", "unknown")
            body = func.get("body", "")
            calls = func.get("calls", [])
            complexity = func.get("complexity", 0)
            dead_imports = func.get("dead_imports", [])
            unused_vars = func.get("unused_vars", [])
            placebo = func.get("placebo_calls", [])

            if body.strip() in ("pass", "...", "raise NotImplementedError"):
                module_findings.append(CargoCultFinding(
                    name=f"{name}.{func_name}", finding_type="stub",
                    severity=0.8, description="Empty stub masquerading as implementation",
                    evidence=[f"body: {body.strip()[:50]}"]
                ))

            if len(calls) == 0 and complexity > 3:
                module_findings.append(CargoCultFinding(
                    name=f"{name}.{func_name}", finding_type="complex_noop",
                    severity=0.6, description="Complex function with no external calls",
                    evidence=[f"complexity={complexity}", f"calls={calls}"]
                ))

            if dead_imports:
                module_findings.append(CargoCultFinding(
                    name=f"{name}.{func_name}", finding_type="dead_import",
                    severity=0.3, description=f"Unused imports: {dead_imports}",
                    evidence=[f"dead_imports={dead_imports}"]
                ))

            if unused_vars:
                module_findings.append(CargoCultFinding(
                    name=f"{name}.{func_name}", finding_type="unused_vars",
                    severity=0.4, description=f"Unused variables: {unused_vars}",
                    evidence=[f"unused={unused_vars}"]
                ))

            if placebo:
                module_findings.append(CargoCultFinding(
                    name=f"{name}.{func_name}", finding_type="placebo",
                    severity=0.7, description=f"Placebo calls: {placebo}",
                    evidence=[f"placebo={placebo}"]
                ))

            if body.count("print") > 3 and complexity < 2:
                module_findings.append(CargoCultFinding(
                    name=f"{name}.{func_name}", finding_type="print_only",
                    severity=0.5, description="Function only prints, no real logic",
                    evidence=[f"print_count={body.count('print')}", f"complexity={complexity}"]
                ))

        self.findings.extend(module_findings)
        return module_findings

    def summary(self) -> Dict:
        type_counts = {}
        for f in self.findings:
            type_counts[f.finding_type] = type_counts.get(f.finding_type, 0) + 1
        avg_severity = sum(f.severity for f in self.findings) / max(len(self.findings), 1)
        return {
            "modules_scanned": len(self.scanned_modules),
            "total_findings": len(self.findings),
            "findings_by_type": type_counts,
            "avg_severity": round(avg_severity, 3),
            "high_severity": sum(1 for f in self.findings if f.severity > 0.6),
            "top_findings": [
                {"name": f.name, "type": f.finding_type, "severity": f.severity}
                for f in sorted(self.findings, key=lambda x: x.severity, reverse=True)[:5]
            ],
        }


def demo():
    detector = CargoCultDetector()
    print("=== Cargo Cult Detector ===")

    modules_data = {
        "analytics": [
            {"name": "compute_metrics", "body": "pass", "calls": [],
             "complexity": 1, "dead_imports": ["numpy"], "unused_vars": [], "placebo_calls": []},
            {"name": "real_analysis", "body": "return sum(data)/len(data)",
             "calls": ["sum", "len"], "complexity": 2, "dead_imports": [],
             "unused_vars": [], "placebo_calls": []},
            {"name": "fake_validator", "body": "print('valid'); print('ok'); print('done')",
             "calls": [], "complexity": 1, "dead_imports": [],
             "unused_vars": ["temp"], "placebo_calls": ["validate"]},
        ],
        "helpers": [
            {"name": "placeholder", "body": "raise NotImplementedError",
             "calls": [], "complexity": 0, "dead_imports": ["os"],
             "unused_vars": [], "placebo_calls": []},
            {"name": "useful_func", "body": "return x + y",
             "calls": [], "complexity": 1, "dead_imports": [],
             "unused_vars": [], "placebo_calls": []},
        ],
    }

    for module_name, functions in modules_data.items():
        findings = detector.scan_module(module_name, functions)
        print(f"\n  {module_name}: {len(findings)} findings")
        for f in findings:
            print(f"    [{f.finding_type}] {f.name}: {f.description} "
                  f"(severity={f.severity})")

    summary = detector.summary()
    print(f"\nSummary:")
    print(f"  Modules scanned: {summary['modules_scanned']}")
    print(f"  Total findings: {summary['total_findings']}")
    print(f"  By type: {summary['findings_by_type']}")
    print(f"  High severity: {summary['high_severity']}")

    return summary


if __name__ == "__main__":
    demo()
