"""Fail-closed, read-only policy wrappers for Atlas tracing and KG validation.

The whole_atlas_authorized and sandbox_verified flags are configuration gates,
not identity proof or OS-level sandbox attestations. Callers must establish those
trust decisions outside this module.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, FrozenSet, Optional, Set


class WrapperError(Exception):
    """Structured policy rejection with a stable machine-readable code."""

    def __init__(self, code: str, details: Dict[str, Any]):
        self.code = code
        self.details = details
        super().__init__(f"[{code}] {json.dumps(details, sort_keys=True)}")


def emit_log(wrapper_id: str, event_type: str, user_intent: str,
             scope_mode: str, skill_consulted: Optional[str], result: str) -> Dict[str, Any]:
    """Create a structured log event; persistence/tamper protection is external."""
    safe_intent = user_intent if isinstance(user_intent, str) else ""
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wrapper_id": wrapper_id,
        "event_type": event_type,
        # Avoid retaining potentially sensitive free-text prompts in audit logs.
        "intent_sha256": hashlib.sha256(safe_intent.encode("utf-8")).hexdigest(),
        "intent_length": len(safe_intent) if isinstance(user_intent, str) else None,
        "scope_mode": scope_mode,
        "skill_consulted": skill_consulted,
        "result": result,
    }


def reject(wrapper_id: str, skill_name: str, intent: str, scope_mode: str,
           code: str, result: str, **details: Any) -> None:
    log = emit_log(wrapper_id, "ERROR", intent, scope_mode, skill_name, result)
    raise WrapperError(code, {**details, "log": log})


def validate_scope(wrapper_id: str, skill_name: str, intent: str,
                   scope_mode: str, allowed_scopes: FrozenSet[str]) -> None:
    if not isinstance(intent, str) or not intent.strip() or len(intent) > 512:
        reject(wrapper_id, skill_name, str(intent), str(scope_mode),
               "INVALID_INTENT", "INVALID_INTENT",
               description="Intent must be a non-empty string of at most 512 characters.")
    if not isinstance(scope_mode, str) or scope_mode not in allowed_scopes:
        reject(wrapper_id, skill_name, intent, str(scope_mode),
               "INVALID_SCOPE_MODE", "INVALID_SCOPE",
               supplied_scope=repr(scope_mode), allowed_scopes=sorted(allowed_scopes))


def validate_operation(wrapper_id: str, skill_name: str, intent: str,
                       scope_mode: str, operation: Optional[str],
                       allowed_operations: FrozenSet[str]) -> None:
    # Omission preserves the original API; in that case the selected scope is
    # the effective operation. An explicit operation must match it exactly.
    effective_operation = scope_mode if operation is None else operation
    if (not isinstance(effective_operation, str)
            or effective_operation not in allowed_operations
            or effective_operation != scope_mode):
        reject(wrapper_id, skill_name, intent, scope_mode,
               "REJECTED_OPERATION", "REJECTED_OPERATION",
               operation=repr(operation), expected_operation=scope_mode,
               allowed_operations=sorted(allowed_operations),
               reason="Operation must be explicitly permitted and match the selected scope.")


class AtlasTraceWrapper:
    _POLICY_FIELDS = frozenset({"_whole_atlas_authorized", "_accessible_pages"})
    ALLOWED_SCOPES = frozenset({"ANCHORED_TRACE", "READ_ONLY_WHOLE_ATLAS_SCAN"})
    ALLOWED_OPERATIONS = ALLOWED_SCOPES
    DEFAULT_PAGES = frozenset({"MEM-KG0001-CORE", "ECHO-WAL-001"})

    def __init__(self, accessible_pages: Optional[Set[str]] = None,
                 whole_atlas_authorized: bool = False):
        if type(whole_atlas_authorized) is not bool:
            raise TypeError("whole_atlas_authorized must be a bool")
        pages = self.DEFAULT_PAGES if accessible_pages is None else accessible_pages
        if isinstance(pages, (str, bytes)) or any(
                not isinstance(page, str) or not page.strip() for page in pages):
            raise ValueError("accessible_pages must contain non-empty strings")
        self.wrapper_id = "atlas-trace-wrapper"
        self.skill_name = "Trace-Atlas-Paradoxes"
        self._whole_atlas_authorized = whole_atlas_authorized
        self._accessible_pages = frozenset(pages)
        self._policy_sealed = True

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_policy_sealed", False) and name in self._POLICY_FIELDS:
            raise AttributeError(f"{name} is immutable after initialization")
        object.__setattr__(self, name, value)

    @property
    def whole_atlas_authorized(self) -> bool:
        return self._whole_atlas_authorized

    @property
    def accessible_pages(self) -> FrozenSet[str]:
        return self._accessible_pages

    def execute(self, intent: str, scope_mode: str, anchor: Optional[str] = None,
                operation: Optional[str] = None,
                input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        validate_scope(self.wrapper_id, self.skill_name, intent, scope_mode, self.ALLOWED_SCOPES)
        validate_operation(self.wrapper_id, self.skill_name, intent, scope_mode,
                           operation, self.ALLOWED_OPERATIONS)

        if scope_mode == "ANCHORED_TRACE":
            if not isinstance(anchor, str) or not anchor.strip():
                reject(self.wrapper_id, self.skill_name, intent, scope_mode,
                       "MISSING_ANCHOR", "MISSING_ANCHOR",
                       description="An anchored trace requires a non-empty anchor.",
                       next_step="Specify the exact object to trace.")
            if anchor not in self.accessible_pages:
                reject(self.wrapper_id, self.skill_name, intent, scope_mode,
                       "MISSING_ACCESS", "MISSING_ACCESS", source=repr(anchor),
                       description="The requested page is not accessible.",
                       next_step="Provide authorized access or supply the content.")
        else:
            if anchor is not None:
                reject(self.wrapper_id, self.skill_name, intent, scope_mode,
                       "INVALID_PARAMETERS", "INVALID_PARAMETERS",
                       description="Whole-atlas scans cannot accept individual anchors.")
            if not self.whole_atlas_authorized:
                reject(self.wrapper_id, self.skill_name, intent, scope_mode,
                       "MISSING_ACCESS", "MISSING_ACCESS",
                       description="Caller lacks explicit whole-atlas authorization.",
                       next_step="Obtain an externally authenticated auditor grant.")

        if input_data is not None and not isinstance(input_data, dict):
            reject(self.wrapper_id, self.skill_name, intent, scope_mode,
                   "SKILL_LOGIC_VIOLATION", "SKILL_LOGIC_VIOLATION",
                   description="input_data must be a dictionary.")
        if input_data is not None and "invalid_schema_key" in input_data:
            reject(self.wrapper_id, self.skill_name, intent, scope_mode,
                   "SKILL_LOGIC_VIOLATION", "SKILL_LOGIC_VIOLATION",
                   description="Input contains a prohibited schema key.",
                   expected_structure=["Nodes", "Connections", "Paradoxes", "Confidence"])
        return emit_log(self.wrapper_id, "INFO", intent, scope_mode, self.skill_name, "SUCCESS")


class KGValidationWrapper:
    _POLICY_FIELDS = frozenset({"_sandbox_verified", "_accessible_schemas"})
    ALLOWED_SCOPES = frozenset({"STATIC_ANALYSIS", "TRANSACTION_VALIDATION"})
    ALLOWED_OPERATIONS = ALLOWED_SCOPES
    DEFAULT_SCHEMAS = frozenset({"WAL_ENTRY_SCHEMA"})

    def __init__(self, sandbox_verified: bool = False,
                 accessible_schemas: Optional[Set[str]] = None):
        if type(sandbox_verified) is not bool:
            raise TypeError("sandbox_verified must be a bool")
        schemas = self.DEFAULT_SCHEMAS if accessible_schemas is None else accessible_schemas
        if isinstance(schemas, (str, bytes)) or any(
                not isinstance(schema, str) or not schema.strip() for schema in schemas):
            raise ValueError("accessible_schemas must contain non-empty strings")
        self.wrapper_id = "kg-validation-wrapper"
        self.skill_name = "Validate-KG-Transactions"
        self._sandbox_verified = sandbox_verified
        self._accessible_schemas = frozenset(schemas)
        self._policy_sealed = True

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_policy_sealed", False) and name in self._POLICY_FIELDS:
            raise AttributeError(f"{name} is immutable after initialization")
        object.__setattr__(self, name, value)

    @property
    def sandbox_verified(self) -> bool:
        return self._sandbox_verified

    @property
    def accessible_schemas(self) -> FrozenSet[str]:
        return self._accessible_schemas

    def execute(self, intent: str, scope_mode: str, operation: Optional[str] = None,
                execute_code: bool = False, schema_id: Optional[str] = None) -> Dict[str, Any]:
        validate_scope(self.wrapper_id, self.skill_name, intent, scope_mode, self.ALLOWED_SCOPES)
        validate_operation(self.wrapper_id, self.skill_name, intent, scope_mode,
                           operation, self.ALLOWED_OPERATIONS)
        if type(execute_code) is not bool:
            reject(self.wrapper_id, self.skill_name, intent, scope_mode,
                   "INVALID_EXECUTION_FLAG", "INVALID_EXECUTION_FLAG",
                   description="execute_code must be a boolean.")
        if execute_code and scope_mode == "STATIC_ANALYSIS":
            reject(self.wrapper_id, self.skill_name, intent, scope_mode,
                   "EXECUTION_SCOPE_MISMATCH", "EXECUTION_SCOPE_MISMATCH",
                   description="STATIC_ANALYSIS is non-executing; code execution is forbidden in this scope.")
        if execute_code and not self.sandbox_verified:
            reject(self.wrapper_id, self.skill_name, intent, scope_mode,
                   "SANDBOX_UNAVAILABLE", "SANDBOX_UNAVAILABLE",
                   description="Code execution requires a verified disposable sandbox.",
                   next_step="Use static analysis or verify the sandbox externally.")
        if schema_id is not None and (
                not isinstance(schema_id, str) or schema_id not in self.accessible_schemas):
            reject(self.wrapper_id, self.skill_name, intent, scope_mode,
                   "MISSING_ACCESS", "MISSING_ACCESS", source=repr(schema_id),
                   description="The requested schema is not accessible.",
                   next_step="Provide authorized access to the schema.")
        return emit_log(self.wrapper_id, "INFO", intent, scope_mode, self.skill_name, "SUCCESS")
