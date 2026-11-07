# IXPANSION Local Workbench Architecture

## Purpose
A portable workbench for repository inspection, controlled changes, experiments, reusable skills, and cross-platform project knowledge.

## System layers
1. Repository: GitHub canonical code; GitLab is a secondary source-control adapter.
2. Workspace: local checkouts, scratch experiments, generated artifacts.
3. Knowledge: Notion decisions, runbooks, project records, skill catalog.
4. Artifacts: Google Drive, Dropbox, and ChatGPT file library.
5. Execution: local execution where available, Vercel sandboxes, Supabase services.
6. Design: Figma and Canva.
7. Media: OpenArt.
8. Orchestration: Composio and custom plugin adapters.
9. Evidence: append-only JSONL records plus CI artifacts and linked source evidence.

## Adapter contract
Every adapter declares stable ID/version, connection state, separate read/write capabilities, required permission names (never secret values), idempotency, pagination, approval class, verification method, and evidence reference.

## Execution lifecycle
DISCOVER -> PLAN -> PREFLIGHT -> APPROVAL (if needed) -> EXECUTE -> VERIFY -> RECORD.

Stop on missing authorization, unknown target identity, ambiguous destructive scope, failed preflight, or unverifiable outcome.

## Evidence record
Record timestamp, actor/tool, target, action, input digest, status, verification method, output references, and redaction notes. Never store access tokens, private keys, passwords, or raw environment values.

## Persistence model
The repository contains portable manifests and skills. Notion stores durable project knowledge. Google Drive/Dropbox store user-facing documents and artifacts. Supabase is optional runtime persistence, not the source of truth for code or evidence. Vercel is a deployment target, not the canonical repository.

## Environment limitation
A ChatGPT execution folder is not automatically a persistent Codespace on the user's device. Export or synchronize it to a durable repository/workspace before assuming cross-session persistence.
