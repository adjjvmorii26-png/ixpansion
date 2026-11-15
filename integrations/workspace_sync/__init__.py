"""IXPANSION Notion + Google Workspace synchronization primitives."""

from .outbox import (
    Adapter,
    IdempotencyConflict,
    InvalidEvent,
    PermanentAdapterError,
    TransientAdapterError,
    WorkspaceOutbox,
    WorkspaceSyncError,
    WorkspaceSyncRunner,
)

__all__ = [
    "Adapter",
    "IdempotencyConflict",
    "InvalidEvent",
    "PermanentAdapterError",
    "TransientAdapterError",
    "WorkspaceOutbox",
    "WorkspaceSyncError",
    "WorkspaceSyncRunner",
]
