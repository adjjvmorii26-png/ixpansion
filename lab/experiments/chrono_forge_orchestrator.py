#!/usr/bin/env python3
"""Chrono Forge Orchestrator — unified pipeline for chrono_forge agents.

Bridges wanderer + sentinel + mimic + forge_mind + echo_vault into a
single orchestrated pipeline. The orchestrator:
1. Wanderer proposes new experiment names
2. Forge Mind triages them by ritual type
3. Sentinel validates structural integrity
4. Mimic learns from the output pattern
5. Echo Vault records the entire pipeline run

This creates a reproducible "creation ritual" that generates,
validates, and archives new experimental modules.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any


STEMS = ["echo", "flux", "glyph", "orbit", "prism", "quill", "rift", "spark", "tide", "vault"]
MODES = ["bind", "fold", "mesh", "scan", "seal", "tune", "weave", "yield"]
RITUALS = {
    "error": ("repair", "fracture detected; bind a reversible seam"),
    "status": ("observe", "collapse the signal into an inspectable ledger"),
    "design": ("shape", "draft a bounded prototype before expansion"),
    "expand": ("branch", "grow only through an isolated shadow lane"),
}


@dataclass
class PipelineStep:
    agent: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    success: bool
    duration_ms: float = 0.0

    def payload(self) -> dict[str, Any]:
        return {
            "agent": self.agent,
            "success": self.success,
            "output_keys": list(self.output_data.keys()),
        }


@dataclass
class ChronoForgeOrchestrator:
    """Unified pipeline for chrono_forge agent ecosystem."""
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = __import__("random").Random(self.seed)
        self._pipeline_log: list[dict[str, Any]] = []

    def run_pipeline(self, seed_phrase: str = "status check") -> dict[str, Any]:
        steps: list[PipelineStep] = []

        # Step 1: Wanderer proposes names
        wanderer_output = self._wanderer_step(seed_phrase)
        steps.append(PipelineStep(
            agent="wanderer", input_data={"phrase": seed_phrase},
            output_data=wanderer_output, success=True,
        ))

        # Step 2: Forge Mind triages
        forge_output = self._forge_mind_step(seed_phrase)
        steps.append(PipelineStep(
            agent="forge_mind", input_data={"phrase": seed_phrase},
            output_data=forge_output, success=True,
        ))

        # Step 3: Sentinel validates
        sentinel_output = self._sentinel_step(wanderer_output)
        steps.append(PipelineStep(
            agent="sentinel", input_data={"proposals": wanderer_output.get("count", 0)},
            output_data=sentinel_output, success=sentinel_output.get("valid", False),
        ))

        # Step 4: Mimic learns
        mimic_output = self._mimic_step(steps)
        steps.append(PipelineStep(
            agent="mimic", input_data={"step_count": len(steps)},
            output_data=mimic_output, success=True,
        ))

        # Step 5: Echo Vault records
        vault_output = self._echo_vault_step(steps)
        steps.append(PipelineStep(
            agent="echo_vault", input_data={"pipeline_steps": len(steps)},
            output_data=vault_output, success=True,
        ))

        pipeline_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "seed_phrase": seed_phrase,
            "steps": [s.payload() for s in steps],
            "all_success": all(s.success for s in steps),
            "pipeline_hash": hashlib.sha256(
                json.dumps([s.payload() for s in steps], sort_keys=True).encode()
            ).hexdigest()[:16],
        }
        self._pipeline_log.append(pipeline_record)
        return pipeline_record

    def _wanderer_step(self, phrase: str) -> dict[str, Any]:
        ts = datetime.now(timezone.utc).isoformat()
        h = hashlib.sha256(ts.encode()).hexdigest()
        proposals = []
        for i in range(3):
            chunk = h[i * 4: i * 4 + 8]
            stem = STEMS[int(chunk[:2], 16) % len(STEMS)]
            mode = MODES[int(chunk[2:4], 16) % len(MODES)]
            name = f"{stem}_{mode}_{chunk[4:].lower()}"
            proposals.append({"module": name, "sigil": f"0x{chunk.upper()}"})
        return {"agent": "wanderer", "proposals": proposals, "count": len(proposals)}

    def _forge_mind_step(self, phrase: str) -> dict[str, Any]:
        normalized = " ".join(phrase.lower().split())
        ritual, response = next(
            ((ritual, resp) for token, (ritual, resp) in RITUALS.items() if token in normalized),
            ("witness", "preserve the phrase as an unresolved anomaly"),
        )
        return {"agent": "forge_mind", "ritual": ritual, "response": response}

    def _sentinel_step(self, wanderer_output: dict) -> dict[str, Any]:
        proposals = wanderer_output.get("proposals", [])
        valid = all(
            len(p.get("module", "")) > 5 and p.get("sigil", "").startswith("0x")
            for p in proposals
        )
        return {
            "agent": "sentinel",
            "valid": valid,
            "checked": len(proposals),
            "integrity_score": 1.0 if valid else 0.5,
        }

    def _mimic_step(self, steps: list[PipelineStep]) -> dict[str, Any]:
        pattern = " → ".join(s.agent for s in steps)
        sigil = hashlib.sha256(pattern.encode()).hexdigest()[:8]
        return {
            "agent": "mimic",
            "learned_pattern": pattern,
            "sigil": sigil,
            "pattern_length": len(steps),
        }

    def _echo_vault_step(self, steps: list[PipelineStep]) -> dict[str, Any]:
        entry_count = len(self._pipeline_log) + 1
        return {
            "agent": "echo_vault",
            "vault_entry": entry_count,
            "recorded_agents": [s.agent for s in steps],
        }

    def history_summary(self) -> dict[str, Any]:
        return {
            "total_runs": len(self._pipeline_log),
            "success_rate": sum(1 for p in self._pipeline_log if p["all_success"]) / max(1, len(self._pipeline_log)),
            "unique_agents": list(set(
                step["agent"]
                for run in self._pipeline_log
                for step in run["steps"]
            )),
        }


def demo() -> dict[str, Any]:
    orch = ChronoForgeOrchestrator(seed=42)
    result1 = orch.run_pipeline("error detected in lattice")
    result2 = orch.run_pipeline("expand the frontier")
    return {
        "runs": [result1, result2],
        "history": orch.history_summary(),
    }


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
