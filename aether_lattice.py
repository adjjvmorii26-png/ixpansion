"""Foundation coordinator for the IXPANSION agent, lattice, trust, and federation layers."""

from __future__ import annotations

import hashlib
import os
import re
import uuid
from copy import deepcopy
from typing import Any, Optional

from agent import Agent
from federated_stack import run_1_3_stack
from lattice_stack import MachineLattice
from security_controls import AuditStore, TrustStore


class AetherLattice:
    """Compose the offline project layers into one inspectable runtime."""

    DATA_KEY_LIMIT = 128
    RECYCLE_TEXT_LIMIT = 50_000
    RECYCLE_CHUNK_LIMITS = (64, 4_096)
    RETRIEVE_TOKEN_LIMITS = (1, 8_000)

    WORKFLOWS = {
        "summarize": {
            "description": "Create a compact summary from the first sentence.",
            "skill": "summarize",
        },
        "extract_tasks": {
            "description": "Extract checklist, TODO, and Task lines.",
            "skill": "tasks",
        },
        "make_checklist": {
            "description": "Turn each non-empty line into an unchecked item.",
            "skill": "checklist",
        },
        "score_priority": {
            "description": "Classify work as high, medium, or low priority.",
            "skill": "priority",
        },
        "normalize_text": {
            "description": "Collapse noisy whitespace into one readable line.",
            "skill": "normalize",
        },
        "dispatch_work": {
            "description": "Allocate safe capacity and run the agent plan.",
            "skill": None,
        },
    }

    def __init__(
        self,
        agent: Optional[Agent] = None,
        lattice: Optional[MachineLattice] = None,
        trust: Optional[TrustStore] = None,
        audits: Optional[AuditStore] = None,
    ):
        self.agent = agent or Agent(name="aether-agent")
        self.lattice = lattice or MachineLattice()
        self.trust = trust or TrustStore()
        self.audits = audits or AuditStore(":memory:")
        self.data: dict[str, Any] = {}

    def list_data(self) -> list[str]:
        return sorted(self.data)

    @classmethod
    def _normalize_data_key(cls, key: str) -> str:
        if not isinstance(key, str):
            raise ValueError("data key must be text")
        normalized = key.strip()
        if not normalized:
            raise ValueError("data key is required")
        if len(normalized) > cls.DATA_KEY_LIMIT:
            raise ValueError(f"data key must be {cls.DATA_KEY_LIMIT} characters or fewer")
        if any(
            character.isspace() or character in "/\\" or ord(character) < 32
            for character in normalized
        ):
            raise ValueError("data key cannot contain whitespace or path separators")
        return normalized

    def save_data(self, key: str, value: Any) -> dict[str, Any]:
        normalized_key = self._normalize_data_key(key)
        self.data[normalized_key] = deepcopy(value)
        return {"key": normalized_key, "value": deepcopy(self.data[normalized_key])}

    def recycle_data(
        self,
        text: str,
        *,
        chunk_size: int = 800,
        task_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Compile raw text into bounded, reusable context without retaining raw input."""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text is required")
        if len(text) > self.RECYCLE_TEXT_LIMIT:
            raise ValueError(
                f"text must be {self.RECYCLE_TEXT_LIMIT} characters or fewer"
            )
        minimum, maximum = self.RECYCLE_CHUNK_LIMITS
        if not isinstance(chunk_size, int) or not minimum <= chunk_size <= maximum:
            raise ValueError(f"chunk_size must be between {minimum} and {maximum}")

        redacted_result = self.agent.redact_secrets(text)
        redacted = text if redacted_result == "Redacted: no secrets found." else redacted_result
        deduplicated = self.agent.deduplicate_lines(redacted)
        normalized = " ".join(deduplicated.split())
        summary = self.agent.summarize(normalized)
        chunks = self._chunk_context(normalized, chunk_size)
        artifact = {
            "summary": summary.removeprefix("Summary: "),
            "chunks": chunks,
            "source_sha256": hashlib.sha256(redacted.encode("utf-8")).hexdigest(),
            "characters": len(normalized),
            "approximate_tokens": max(1, (len(normalized) + 3) // 4),
            "chunk_size": chunk_size,
            "redacted": redacted_result != "Redacted: no secrets found.",
        }
        data_key = task_id or "recycle:latest"
        self.save_data(data_key, artifact)
        return {"data_key": self._normalize_data_key(data_key), **artifact}

    @staticmethod
    def _chunk_context(text: str, chunk_size: int) -> list[str]:
        """Split context at whitespace where possible without exceeding the limit."""
        chunks = []
        remaining = text
        while remaining:
            if len(remaining) <= chunk_size:
                chunks.append(remaining)
                break
            cut = remaining.rfind(" ", 0, chunk_size + 1)
            if cut <= 0:
                cut = chunk_size
            chunks.append(remaining[:cut].rstrip())
            remaining = remaining[cut:].lstrip()
        return chunks

    def load_data(self, key: str) -> Any:
        normalized_key = self._normalize_data_key(key)
        if normalized_key not in self.data:
            raise KeyError(f"No reusable data named: {normalized_key}")
        return deepcopy(self.data[normalized_key])

    def retrieve_context(
        self,
        key: str,
        *,
        query: str = "",
        max_tokens: int = 800,
    ) -> dict[str, Any]:
        """Return the most relevant stored chunks within an approximate token budget."""
        minimum, maximum = self.RETRIEVE_TOKEN_LIMITS
        if not isinstance(max_tokens, int) or not minimum <= max_tokens <= maximum:
            raise ValueError(f"max_tokens must be between {minimum} and {maximum}")
        artifact = self.load_data(key)
        if not isinstance(artifact, dict) or not isinstance(artifact.get("chunks"), list):
            raise ValueError("data key does not contain recyclable context")
        query_terms = set(re.findall(r"[a-z0-9]+", query.casefold()))
        ranked = []
        for index, chunk in enumerate(artifact["chunks"]):
            if not isinstance(chunk, str):
                continue
            chunk_terms = set(re.findall(r"[a-z0-9]+", chunk.casefold()))
            score = len(query_terms & chunk_terms)
            ranked.append((0 if score else 1, -score, index, chunk))
        ranked.sort()
        selected = []
        used_tokens = 0
        for _, _, _, chunk in ranked:
            chunk_tokens = max(1, (len(chunk) + 3) // 4)
            if selected and used_tokens + chunk_tokens > max_tokens:
                continue
            if not selected and chunk_tokens > max_tokens:
                chunk = chunk[: max_tokens * 4]
                chunk_tokens = max_tokens
            selected.append(chunk)
            used_tokens += chunk_tokens
        normalized_key = self._normalize_data_key(key)
        return {
            "data_key": normalized_key,
            "query": query,
            "chunks": selected,
            "approximate_tokens": used_tokens,
            "max_tokens": max_tokens,
        }

    def workflows(self) -> list[dict[str, str]]:
        return [
            {"name": name, "description": details["description"]}
            for name, details in self.WORKFLOWS.items()
        ]

    def run_workflow(
        self,
        workflow: str,
        text: str,
        *,
        critical: bool = False,
        lease_seconds: Optional[float] = None,
        operator: str = "aether",
        task_id: Optional[str] = None,
    ) -> dict[str, Any]:
        details = self.WORKFLOWS.get(workflow)
        if details is None:
            available = ", ".join(self.WORKFLOWS)
            raise ValueError(f"Unknown workflow '{workflow}'. Available: {available}")
        if not text.strip():
            raise ValueError("text is required")
        if details["skill"] is None:
            result = self.dispatch(
                text,
                critical=critical,
                lease_seconds=lease_seconds,
                operator=operator,
                task_id=task_id,
            )
        else:
            result = {
                "workflow": workflow,
                "input": text,
                "result": self.agent.use_skill(details["skill"], text),
            }
        data_key = task_id or f"workflow:{workflow}:latest"
        self.save_data(data_key, result)
        return {**result, "data_key": data_key}

    def snapshot(self) -> dict[str, Any]:
        federation = run_1_3_stack(
            green_scores={
                machine_id: machine.health
                for machine_id, machine in self.lattice.machines.items()
            }
            or None
        )
        return {
            "name": "aether-lattice",
            "version": "0.1",
            "agent": {
                "name": self.agent.name,
                "memory_entries": len(self.agent.memory),
                "history_entries": len(self.agent.history),
                "skills": len(self.agent.skills),
            },
            "lattice": self.lattice.snapshot(),
            "federation": {
                "primary_carbon_federate": federation["primary_carbon_federate"],
                "winner_cluster": federation["si"]["winner_cluster"],
                "best_fitness": federation["si"]["best_fitness"],
                "transport": federation["transport"],
            },
            "trust": {
                "known_subjects": len(self.trust.values),
                "foundation": self.trust.trust("agent:aether"),
            },
            "safety": {
                "audit_records": len(self.audits.decisions()),
                "protected_gate_actions": ["PROD_DEPLOY", "SECRET_ROTATE"],
            },
            "data": {
                "records": len(self.data),
                "keys": self.list_data(),
            },
            "swarm": {
                "role": os.getenv("SWARM_ROLE", "foundation"),
                "token_required": bool(os.getenv("SWARM_TOKEN")),
            },
        }

    def dispatch(
        self,
        task: str,
        *,
        critical: bool = False,
        lease_seconds: Optional[float] = None,
        operator: str = "aether",
        task_id: Optional[str] = None,
    ) -> dict[str, Any]:
        if not task.strip():
            raise ValueError("task is required")
        correlation_id = task_id or uuid.uuid4().hex
        if lease_seconds is None:
            machine_id = self.lattice.allocate(task, critical=critical)
            lease = None
        else:
            lease = self.lattice.acquire(
                task,
                duration=lease_seconds,
                critical=critical,
            )
            machine_id = lease.machine_id
        node_trust = self.trust.observe(f"node:{machine_id}", True)
        self.audits.record(
            correlation_id,
            {"AETHER_DISPATCH"},
            node_trust,
            operator,
            "ALLOCATED",
            correlation_id=correlation_id,
        )
        result = self.agent.run(task)
        return {
            "task_id": correlation_id,
            "task": task,
            "machine_id": machine_id,
            "critical": critical,
            "lease": None
            if lease is None
            else {"expires_at": lease.expires_at},
            "agent": result,
            "node_trust": node_trust,
        }
