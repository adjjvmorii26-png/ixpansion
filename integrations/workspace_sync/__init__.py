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
from .providers import (
    GoogleDriveMetadataAdapter,
    NotionDatabaseAdapter,
    ProviderConfigurationError,
    ProviderProtocolError,
)

__all__ = [
    "Adapter",
    "GoogleDriveMetadataAdapter",
    "IdempotencyConflict",
    "InvalidEvent",
    "NotionDatabaseAdapter",
    "PermanentAdapterError",
    "ProviderConfigurationError",
    "ProviderProtocolError",
    "TransientAdapterError",
    "WorkspaceOutbox",
    "WorkspaceSyncError",
    "WorkspaceSyncRunner",
]
