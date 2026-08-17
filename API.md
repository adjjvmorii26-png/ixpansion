# IXPANSION API Reference

Complete REST API documentation for IXPANSION with all endpoints, request/response formats, and examples.

## Base URL

```
http://localhost:8000
```

## Authentication

No authentication required for local development. For production deployment:
- Set `X-Swarm-Token` header if `SWARM_TOKEN` environment variable is configured
- All routes return `401 Unauthorized` without the token

## Core Endpoints

### Health & Status

#### GET `/health`
Check API health and readiness.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.2.0-rc3",
  "timestamp": "2026-08-17T12:00:00Z"
}
```

**Status Codes:**
- `200` - API is healthy and ready

---

#### GET `/aether/status`
Get IXPANSION Aether Lattice foundation status.

**Response:**
```json
{
  "agent_name": "aether-agent",
  "skills_available": 25,
  "memory_usage": 4096,
  "lattice_machines": 2,
  "trust_entries": 12,
  "audit_records": 48
}
```

---

## Agent Skills

### GET `/skills`
List all available agent skills.

**Response:**
```json
{
  "skills": [
    {
      "name": "create_outline",
      "description": "Turn non-empty lines into a compact numbered outline",
      "mutates_state": false,
      "network_required": false
    },
    {
      "name": "extract_urls",
      "description": "Extract unique HTTP(S) URLs in first-seen order",
      "mutates_state": false,
      "network_required": false
    }
  ],
  "total": 25
}
```

---

### POST `/skill/{skill_name}`
Execute an agent skill.

**Request:**
```json
{
  "text": "Your input text here"
}
```

**Example: Extract URLs**
```bash
curl -X POST http://localhost:8000/skill/extract_urls \
  -H "Content-Type: application/json" \
  -d '{"text": "Visit https://example.com or http://test.org"}'
```

**Response:**
```json
{
  "skill": "extract_urls",
  "result": "https://example.com\nhttp://test.org",
  "status": "success"
}
```

**Available Skills:**
- `create_outline` - Create numbered outline from lines
- `normalize_text` - Collapse whitespace to single line
- `redact_secrets` - Remove credential-like values
- `sort_tasks` - Sort task lines by priority
- `text_stats` - Report line, word, character counts
- `extract_urls` - Extract HTTP(S) URLs
- `chunk_text` - Split text into fixed-size chunks
- `extract_emails` - Extract email addresses
- `sanitize_filename` - Create valid filename from text
- `word_frequency` - Count words by frequency
- `group_lines` - Group lines by first word
- `hash_text` - Get SHA-256 hash
- `parse_key_values` - Parse key=value lines
- `extract_mentions` - Extract @mentions
- `count_checklist` - Count checked/unchecked items
- `classify_priority` - Classify as high/medium/low
- `is_substantial` - Check if text is substantial
- `deduplicate_lines` - Remove duplicate lines
- `format_checklist` - Format as checklist items
- `dump_memory` - Export current memory
- `summarize` - Create first-sentence summary
- `extract_tasks` - Extract tasks from text
- `is_goal_sufficient` - Check goal detail level
- `ask_tokenrouter` - Query premium TokenRouter model

---

## Aether Lattice Endpoints

### GET `/aether/workflows`
List all available workflows.

**Response:**
```json
{
  "workflows": [
    {
      "name": "process_data",
      "description": "Process raw data through recycling"
    }
  ]
}
```

---

### POST `/aether/dispatch`
Dispatch an allocation to the agent.

**Request:**
```json
{
  "task": "Inspect the mesh",
  "critical": false,
  "lease_seconds": 30
}
```

**Response:**
```json
{
  "task_id": "task-abc123",
  "agent": "aether-agent",
  "plan": ["Understand goal", "Identify resources"],
  "results": ["Initial context loaded"],
  "status": "pending"
}
```

---

### POST `/aether/workflow/{name}`
Execute a named workflow.

**Request:**
```json
{
  "task": "Workflow task description"
}
```

**Response:**
```json
{
  "workflow": "process_data",
  "result": "Processing complete",
  "status": "success"
}
```

---

### GET `/aether/data`
List stored data keys.

**Response:**
```json
{
  "keys": ["context-1", "result-1"],
  "count": 2
}
```

---

### GET `/aether/data/{key}`
Retrieve stored data by key.

**Response:**
```json
{
  "key": "context-1",
  "value": "Stored data content",
  "retrieved_at": "2026-08-17T12:00:00Z"
}
```

---

### PUT `/aether/data/{key}`
Store or update data.

**Request:**
```json
{
  "value": "Data to store"
}
```

**Response:**
```json
{
  "key": "context-1",
  "status": "stored",
  "size_bytes": 256
}
```

---

### POST `/aether/recycle`
Recycle context to remove raw input while preserving reusable chunks.

**Request:**
```json
{
  "text": "Raw text to recycle",
  "chunk_size": 256
}
```

**Response:**
```json
{
  "status": "recycled",
  "chunks_created": 3,
  "keys": ["recycled-1", "recycled-2", "recycled-3"]
}
```

---

### POST `/aether/context/retrieve/{key}`
Retrieve context with budget awareness.

**Request:**
```json
{
  "budget_tokens": 1000
}
```

**Response:**
```json
{
  "key": "recycled-1",
  "content": "Most relevant chunks...",
  "tokens_used": 842,
  "chunks_included": 2
}
```

---

## Resource Management

### GET `/resources`
List all collected resources.

**Response:**
```json
{
  "resources": [
    {
      "id": "resource-abc123",
      "url": "https://example.com/api",
      "collected_at": "2026-08-17T12:00:00Z",
      "size_bytes": 4096
    }
  ],
  "total": 1
}
```

---

### GET `/resources/{resource_id}`
Get a specific resource.

**Response:**
```json
{
  "id": "resource-abc123",
  "url": "https://example.com/api",
  "content": "Resource content...",
  "headers": {"content-type": "application/json"}
}
```

---

### POST `/resources/collect`
Collect a resource from a URL.

**Request:**
```json
{
  "url": "https://api.example.com/data",
  "text": "Optional context"
}
```

**Response:**
```json
{
  "id": "resource-abc123",
  "url": "https://api.example.com/data",
  "status": "collected",
  "size_bytes": 2048
}
```

---

### POST `/resources/jobs`
Submit a resource collection job.

**Request:**
```json
{
  "url": "https://api.example.com/data",
  "text": "Job context"
}
```

**Response:**
```json
{
  "job_id": "job-xyz789",
  "url": "https://api.example.com/data",
  "status": "queued",
  "position": 1
}
```

---

### GET `/resources/jobs/{job_id}`
Get resource job status.

**Response:**
```json
{
  "job_id": "job-xyz789",
  "status": "complete",
  "resource_id": "resource-abc123",
  "completed_at": "2026-08-17T12:00:30Z"
}
```

---

### POST `/resources/jobs/{job_id}/retry`
Retry a failed resource job.

**Response:**
```json
{
  "job_id": "job-xyz789",
  "status": "requeued",
  "position": 2
}
```

---

## Lattice Management

### GET `/lattice/status`
Get machine lattice status.

**Response:**
```json
{
  "machines": [
    {
      "id": "api-healthy-0",
      "health": 0.95,
      "capacity": 0.8,
      "status": "available"
    }
  ],
  "total_machines": 2,
  "healthy_machines": 1,
  "total_capacity": 0.8
}
```

---

### POST `/lattice/heartbeat`
Send machine heartbeat.

**Request:**
```json
{
  "machine_id": "worker-1",
  "health": 0.85,
  "capacity": 0.7,
  "trust": 0.9,
  "load": 0.3
}
```

**Response:**
```json
{
  "machine_id": "worker-1",
  "status": "acknowledged",
  "lease_seconds": 30
}
```

---

### POST `/lattice/allocate`
Allocate work to the lattice.

**Request:**
```json
{
  "task": "Process data",
  "critical": false,
  "lease_seconds": 60
}
```

**Response:**
```json
{
  "task_id": "task-abc123",
  "machine_id": "api-healthy-0",
  "status": "allocated",
  "lease_until": "2026-08-17T12:01:00Z"
}
```

---

## Dashboard

### GET `/dashboard`
Get interactive HTML dashboard.

**Response:** HTML with embedded visualization of:
- Agent status
- Skill usage statistics
- Lattice machine health
- Trust scores
- Recent activities

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request format or missing required field"
}
```

### 404 Not Found
```json
{
  "detail": "Resource or endpoint not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Unexpected server error"
}
```

---

## Rate Limiting

No rate limiting in development. Production deployments should add:
- Per-IP rate limits
- Token bucket algorithm
- Graceful degradation under load

---

## Timeout Behavior

- Skill execution: 30 seconds default
- Resource collection: 60 seconds default
- Lattice heartbeat: 30-second lease window
- Context retrieval: Token budget enforced

---

## Examples

### Example 1: Extract and Store
```bash
# Extract URLs from text
curl -X POST http://localhost:8000/skill/extract_urls \
  -H "Content-Type: application/json" \
  -d '{"text": "Check https://example.com and https://docs.example.com"}'

# Store the result
curl -X PUT http://localhost:8000/aether/data/urls \
  -H "Content-Type: application/json" \
  -d '{"value": "https://example.com\nhttps://docs.example.com"}'
```

### Example 2: Dispatch and Recycle
```bash
# Dispatch a task
curl -X POST http://localhost:8000/aether/dispatch \
  -H "Content-Type: application/json" \
  -d '{"task": "Analyze the mesh", "critical": false}'

# Recycle raw input to remove sensitive data
curl -X POST http://localhost:8000/aether/recycle \
  -H "Content-Type: application/json" \
  -d '{"text": "User input with secrets", "chunk_size": 256}'
```

### Example 3: Resource Collection
```bash
# Collect a resource
curl -X POST http://localhost:8000/resources/collect \
  -H "Content-Type: application/json" \
  -d '{"url": "https://api.example.com/data"}'

# Or submit a background job
curl -X POST http://localhost:8000/resources/jobs \
  -H "Content-Type: application/json" \
  -d '{"url": "https://api.example.com/data"}'
```

---

## Environment Variables

- `IXPANSION_RESOURCE_HOSTS` - Comma-separated list of allowed resource URLs
- `IXPANSION_RESOURCE_DB` - Path to resource storage database
- `IXPANSION_RESOURCE_WORKERS` - Number of background workers for resource jobs
- `IXPANSION_RESOURCE_MAX_PENDING` - Maximum pending resource jobs in queue
- `IXPANSION_RESOURCE_JOBS_DB` - Path to resource jobs database
- `SWARM_TOKEN` - Optional authentication token for swarm endpoints

---

## See Also

- [README.md](README.md) - Architecture and quick start
- [AGENTS.md](AGENTS.md) - Agent and workforce documentation
- [api/main.py](api/main.py) - API implementation source
