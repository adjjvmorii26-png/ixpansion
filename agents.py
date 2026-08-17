#!/usr/bin/env python3
"""IXPANSION Agent definitions and agent factory.

Defines agent archetypes, role specifications, and skill mappings for the
IXPANSION workforce system. Each agent archetype represents a specialized
capability: orchestration, verification, implementation, security, or runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class AgentRole(Enum):
    """Core agent roles in IXPANSION."""

    ORCHESTRATOR = "orchestrator"  # End-to-end capability coordination
    BUILDER = "builder"  # Python implementation and testing
    VERIFIER = "verifier"  # Test, contract, and release validation
    OPERATOR = "operator"  # Runtime, CLI, and integration testing
    CONTRACT_ENGINEER = "contract_engineer"  # API, CLI, and README contracts
    SECURITY = "security"  # Secrets, deps, auth, and audit controls
    MISSION_DIRECTOR = "mission_director"  # Top-level coordination
    COOKIE_HANDLER = "cookie_handler"  # Auth state and session management


class AgentTier(Enum):
    """Coordination tier for agent hierarchy."""

    DIRECTOR = "director"  # Top-level coordinator
    SPECIALIST = "specialist"  # Domain-specific role
    OPERATOR = "operator"  # Runtime execution


class AgentCapability(Enum):
    """Fine-grained skill categories."""

    # Coordination
    ORCHESTRATION = "orchestration"
    DELEGATION = "delegation"
    SEQUENCING = "sequencing"

    # Implementation
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    REFACTORING = "refactoring"
    BUG_FIX = "bug_fix"

    # Testing
    UNIT_TESTING = "unit_testing"
    INTEGRATION_TESTING = "integration_testing"
    REGRESSION_TESTING = "regression_testing"
    CONTRACT_TESTING = "contract_testing"

    # Safety & Security
    SECURITY_AUDIT = "security_audit"
    DEPENDENCY_AUDIT = "dependency_audit"
    SECRET_DETECTION = "secret_detection"
    AUTHORIZATION_CHECK = "authorization_check"

    # Operation
    RUNTIME_DIAGNOSIS = "runtime_diagnosis"
    CLI_TESTING = "cli_testing"
    CONTAINER_ORCHESTRATION = "container_orchestration"
    HEALTH_MONITORING = "health_monitoring"

    # Documentation
    API_DOCUMENTATION = "api_documentation"
    README_SYNC = "readme_sync"
    ARCHITECTURE_DOCUMENTATION = "architecture_documentation"


@dataclass(frozen=True)
class SkillDefinition:
    """A specific skill an agent can perform."""

    name: str
    description: str
    capability: AgentCapability
    requires_network: bool = False
    requires_credentials: bool = False
    is_mutable: bool = False
    estimated_duration_seconds: int = 60


@dataclass(frozen=True)
class AgentSpec:
    """Immutable specification for an IXPANSION agent."""

    name: str
    role: AgentRole
    tier: AgentTier
    description: str
    skills: Set[AgentCapability] = field(default_factory=set)
    can_delegate_to: Set[AgentRole] = field(default_factory=set)
    max_task_complexity: int = 5  # 1-10 scale
    requires_human_approval: bool = False
    requires_test_coverage: bool = True
    offline_capable: bool = True

    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if this agent has a capability."""
        return capability in self.skills

    def can_delegate_to_role(self, role: AgentRole) -> bool:
        """Check if this agent can delegate to another role."""
        return role in self.can_delegate_to


# Agent specifications
MISSION_DIRECTOR_SPEC = AgentSpec(
    name="Mission Director",
    role=AgentRole.MISSION_DIRECTOR,
    tier=AgentTier.DIRECTOR,
    description="Top-level coordinator for complex IXPANSION requests across all layers. Frames missions, inspects context, delegates to specialists, and closes the loop.",
    skills={
        AgentCapability.ORCHESTRATION,
        AgentCapability.DELEGATION,
        AgentCapability.SEQUENCING,
    },
    can_delegate_to={
        AgentRole.ORCHESTRATOR,
        AgentRole.OPERATOR,
        AgentRole.VERIFIER,
        AgentRole.BUILDER,
        AgentRole.CONTRACT_ENGINEER,
        AgentRole.SECURITY,
        AgentRole.COOKIE_HANDLER,
    },
    max_task_complexity=10,
    requires_human_approval=True,
)

ORCHESTRATOR_SPEC = AgentSpec(
    name="Orchestrator",
    role=AgentRole.ORCHESTRATOR,
    tier=AgentTier.SPECIALIST,
    description="Implements end-to-end IXPANSION capabilities across agent, lattice, trust, safety, API, CLI, federation, or workflow layers. Coordinates bounded autonomous changes.",
    skills={
        AgentCapability.ORCHESTRATION,
        AgentCapability.CODE_GENERATION,
        AgentCapability.CODE_REVIEW,
        AgentCapability.SEQUENCING,
    },
    can_delegate_to={
        AgentRole.BUILDER,
        AgentRole.VERIFIER,
        AgentRole.OPERATOR,
    },
    max_task_complexity=9,
    requires_test_coverage=True,
)

BUILDER_SPEC = AgentSpec(
    name="Python Builder",
    role=AgentRole.BUILDER,
    tier=AgentTier.SPECIALIST,
    description="Implements small, maintainable Python changes grounded in observable behavior. Writes focused tests for success, boundary, and failure paths.",
    skills={
        AgentCapability.CODE_GENERATION,
        AgentCapability.CODE_REVIEW,
        AgentCapability.REFACTORING,
        AgentCapability.BUG_FIX,
        AgentCapability.UNIT_TESTING,
        AgentCapability.REGRESSION_TESTING,
    },
    can_delegate_to={
        AgentRole.VERIFIER,
    },
    max_task_complexity=7,
    requires_test_coverage=True,
)

VERIFIER_SPEC = AgentSpec(
    name="Verifier",
    role=AgentRole.VERIFIER,
    tier=AgentTier.SPECIALIST,
    description="Validates tests, contracts, security boundaries, dependencies, compose configuration, and release readiness. Runs focused validation before broader checks.",
    skills={
        AgentCapability.UNIT_TESTING,
        AgentCapability.INTEGRATION_TESTING,
        AgentCapability.CONTRACT_TESTING,
        AgentCapability.SECURITY_AUDIT,
        AgentCapability.DEPENDENCY_AUDIT,
    },
    max_task_complexity=6,
    requires_test_coverage=True,
)

OPERATOR_SPEC = AgentSpec(
    name="Runtime Operator",
    role=AgentRole.OPERATOR,
    tier=AgentTier.SPECIALIST,
    description="Runs commands, smoke-tests routes, exercises the CLI/dashboard, reproduces runtime symptoms, and provides integration testing.",
    skills={
        AgentCapability.RUNTIME_DIAGNOSIS,
        AgentCapability.CLI_TESTING,
        AgentCapability.INTEGRATION_TESTING,
        AgentCapability.HEALTH_MONITORING,
        AgentCapability.CONTAINER_ORCHESTRATION,
    },
    max_task_complexity=5,
    offline_capable=False,
    requires_test_coverage=False,
)

CONTRACT_ENGINEER_SPEC = AgentSpec(
    name="Contract Engineer",
    role=AgentRole.CONTRACT_ENGINEER,
    tier=AgentTier.SPECIALIST,
    description="Manages FastAPI routes, CLI options, dashboard contracts, README documentation, and API schema consistency.",
    skills={
        AgentCapability.CODE_GENERATION,
        AgentCapability.CODE_REVIEW,
        AgentCapability.CONTRACT_TESTING,
        AgentCapability.API_DOCUMENTATION,
        AgentCapability.README_SYNC,
    },
    can_delegate_to={
        AgentRole.VERIFIER,
        AgentRole.OPERATOR,
    },
    max_task_complexity=6,
    requires_test_coverage=True,
)

SECURITY_SPEC = AgentSpec(
    name="Security Guardian",
    role=AgentRole.SECURITY,
    tier=AgentTier.SPECIALIST,
    description="Audits secrets, dependencies, trust gates, audit logging, authorization boundaries, CI/security, and release-security concerns.",
    skills={
        AgentCapability.SECURITY_AUDIT,
        AgentCapability.DEPENDENCY_AUDIT,
        AgentCapability.SECRET_DETECTION,
        AgentCapability.AUTHORIZATION_CHECK,
        AgentCapability.CODE_REVIEW,
    },
    max_task_complexity=7,
    requires_human_approval=True,
    requires_test_coverage=True,
)

COOKIE_HANDLER_SPEC = AgentSpec(
    name="Cookie Eater",
    role=AgentRole.COOKIE_HANDLER,
    tier=AgentTier.SPECIALIST,
    description="Manages browser cookies, sessions, CSRF protection, authentication state, privacy, and cookie-specific tests.",
    skills={
        AgentCapability.CODE_GENERATION,
        AgentCapability.SECURITY_AUDIT,
        AgentCapability.CONTRACT_TESTING,
        AgentCapability.BUG_FIX,
    },
    max_task_complexity=5,
    requires_test_coverage=True,
)

# Registry of all agent specifications
AGENT_REGISTRY: Dict[AgentRole, AgentSpec] = {
    AgentRole.MISSION_DIRECTOR: MISSION_DIRECTOR_SPEC,
    AgentRole.ORCHESTRATOR: ORCHESTRATOR_SPEC,
    AgentRole.BUILDER: BUILDER_SPEC,
    AgentRole.VERIFIER: VERIFIER_SPEC,
    AgentRole.OPERATOR: OPERATOR_SPEC,
    AgentRole.CONTRACT_ENGINEER: CONTRACT_ENGINEER_SPEC,
    AgentRole.SECURITY: SECURITY_SPEC,
    AgentRole.COOKIE_HANDLER: COOKIE_HANDLER_SPEC,
}


@dataclass
class AgentInstance:
    """A running instance of an IXPANSION agent."""

    spec: AgentSpec
    instance_id: str
    created_at: str
    context: Dict[str, Any] = field(default_factory=dict)
    task_queue: List[Dict[str, Any]] = field(default_factory=list)
    completed_tasks: int = 0
    failed_tasks: int = 0
    status: str = "idle"  # idle, working, blocked, error

    def is_available(self) -> bool:
        """Check if agent is available to accept work."""
        return self.status in ("idle", "blocked") and len(self.task_queue) < 10

    def can_perform_task(self, capability: AgentCapability) -> bool:
        """Check if agent can perform a task."""
        return self.spec.has_capability(capability) and self.is_available()


def get_agent_spec(role: AgentRole) -> Optional[AgentSpec]:
    """Retrieve an agent specification by role."""
    return AGENT_REGISTRY.get(role)


def get_agents_by_capability(capability: AgentCapability) -> List[AgentSpec]:
    """Find all agents with a specific capability."""
    return [spec for spec in AGENT_REGISTRY.values() if spec.has_capability(capability)]


def get_agents_by_tier(tier: AgentTier) -> List[AgentSpec]:
    """Find all agents in a specific coordination tier."""
    return [spec for spec in AGENT_REGISTRY.values() if spec.tier == tier]


def can_chain_delegation(from_role: AgentRole, to_role: AgentRole) -> bool:
    """Check if delegation is valid between two agents."""
    from_spec = get_agent_spec(from_role)
    if not from_spec:
        return False
    return from_spec.can_delegate_to_role(to_role)
