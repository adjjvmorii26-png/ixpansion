"""Reusable IXPANSION plugin runtime primitives."""

from .runtime import (
    Adapter,
    ApprovalClass,
    Capability,
    EvidenceLedger,
    ExecutionContext,
    ExecutionResult,
    Outcome,
    PluginRegistry,
    PluginRuntime,
    PolicyError,
    RetryableAdapterError,
)

__all__ = [
    "Adapter", "ApprovalClass", "Capability", "EvidenceLedger",
    "ExecutionContext", "ExecutionResult", "Outcome", "PluginRegistry",
    "PluginRuntime", "PolicyError", "RetryableAdapterError",
]
