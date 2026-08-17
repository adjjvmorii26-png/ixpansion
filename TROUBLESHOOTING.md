# IXPANSION Troubleshooting Guide

Common issues and solutions for IXPANSION development and deployment.

## Setup Issues

### Python Version Error
**Error:** `AttributeError: type object 'X' has no attribute 'Y'`

**Cause:** Using Python < 3.12

**Solution:**
```bash
python --version  # Check version

# Install Python 3.12
# Ubuntu/Debian: sudo apt-get install python3.12
# macOS: brew install python@3.12
# Windows: Download from python.org

# Create new venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Dependency Installation Fails
**Error:** `ModuleNotFoundError: No module named 'X'`

**Cause:** Incomplete or corrupted installation

**Solution:**
```bash
# Clear pip cache
pip cache purge

# Reinstall from scratch
rm -rf .venv
python -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Verify
python -c "import fastapi, uvicorn, dotenv; print('OK')"
```

### Import Path Issues
**Error:** `ModuleNotFoundError: No module named 'agent'`

**Cause:** Running from wrong directory or PYTHONPATH not set

**Solution:**
```bash
# Ensure you're in project root
cd /path/to/ixpansion
pwd  # Should end with /ixpansion

# Test import
python -c "from agent import Agent; print('OK')"

# If still failing, set PYTHONPATH
export PYTHONPATH="${PWD}:$PYTHONPATH"
```

## Running Tests

### Tests Not Found
**Error:** `Ran 0 tests`

**Cause:** Tests directory not recognized as package

**Solution:**
```bash
# Verify tests/__init__.py exists
ls tests/__init__.py

# Run from project root
cd /path/to/ixpansion
python -m unittest discover -s tests -v

# Or run specific test
python -m unittest tests.test_agent.TestAgent.test_list_skills -v
```

### Test Import Errors
**Error:** `ModuleNotFoundError` during test run

**Cause:** Test can't import local modules

**Solution:**
```bash
# Check pytest.ini has correct pythonpath
cat pytest.ini

# Should contain:
# [pytest]
# pythonpath = .

# Run with explicit path
python -m pytest tests/ -v
```

### Test Timeout
**Error:** `TimeoutError` or test hangs

**Cause:** Test is waiting for network or blocking operation

**Solution:**
```python
# Add timeout to test
import unittest
from unittest import TestCase

class TestWithTimeout(TestCase):
    @unittest.timeout(5)  # 5 second timeout
    def test_something(self):
        # Your test
        pass
```

## API Issues

### API Won't Start
**Error:** `Address already in use`

**Cause:** Port 8000 already in use

**Solution:**
```bash
# Find what's using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>

# Or use different port
python -m uvicorn api.main:app --port 8001
```

### API Returns 500 Error
**Error:** `Internal Server Error`

**Cause:** Unhandled exception in route handler

**Solution:**
```bash
# Check logs for full traceback
# Look for line with "raise" or "Exception"

# Run with debug logging
export PYTHONUNBUFFERED=1
python -m uvicorn api.main:app --log-level debug

# Add try-catch for diagnosis
try:
    result = agent.use_skill("skill_name", "input")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

### Slow API Response
**Error:** Requests take > 10 seconds

**Cause:** Resource collection, database query, or network timeout

**Solution:**
```bash
# Profile the request
import time
start = time.time()
# ... your code ...
elapsed = time.time() - start
print(f"Took {elapsed:.2f}s")

# Check database
sqlite3 ixpansion_resources.sqlite3 "SELECT COUNT(*) FROM resources;"

# Optimize query with index
sqlite3 ixpansion_resources.sqlite3 "CREATE INDEX idx_url ON resources(source_url);"
```

## Agent & Workforce Issues

### Agent Skills Not Discovered
**Error:** `Unknown skill: xyz`

**Cause:** Skill method not named correctly

**Solution:**
```python
# Skills must:
# 1. Be methods on Agent class
# 2. Take self and text: str parameters
# 3. Return str

# ✅ Correct
def extract_urls(self, text: str) -> str:
    """Extract URLs from text."""
    return urls

# ❌ Wrong
def extractURLs(self, text):  # Wrong name and type hints
    return urls

# List available skills
agent = Agent()
print(agent.list_skills())
```

### Workforce Task Not Assigned
**Error:** Task stays in PENDING status

**Cause:** No agent has required capability or all agents busy

**Solution:**
```python
from workforce import get_workforce
from agents import AgentCapability, get_agents_by_capability

# Check agents have capability
agents = get_agents_by_capability(AgentCapability.CODE_GENERATION)
print(f"Agents with CODE_GENERATION: {[a.name for a in agents]}")

# Check agent queue
workforce = get_workforce()
for role, agents in workforce.agents.items():
    for agent in agents:
        print(f"{role.value}: {len(agent.task_queue)} tasks queued")
```

### Mission Execution Fails
**Error:** Mission marked as failed

**Cause:** Task failed or dependency not met

**Solution:**
```python
# Check mission status
from mission_director import get_mission_director

director = get_mission_director()
report = director.close_mission(mission_id)

# Inspect failures
for failure in report['evidence'].get('failures', []):
    print(f"Failed: {failure['description']}")
    print(f"Error: {failure['error']}")

# Check task dependencies
task = workforce.tasks.get(failing_task_id)
print(f"Dependencies: {task.dependencies}")
print(f"Completed: {task.task_id in workforce.completed_task_ids}")
```

## Docker Issues

### Docker Build Fails
**Error:** `failed to solve with frontend dockerfile.v0`

**Cause:** Missing base image or network issue

**Solution:**
```bash
# Pull base image explicitly
docker pull python:3.12-slim

# Build with verbose output
docker build --progress=plain -t ixpansion:latest .

# Check internet connection
curl https://registry.hub.docker.com/v2/
```

### Docker Compose Network Error
**Error:** `Name resolution failed for service 'hub'`

**Cause:** Services can't reach each other

**Solution:**
```bash
# Check network exists
docker network ls

# Rebuild from scratch
docker-compose down -v
docker-compose up

# Check container connectivity
docker exec worker ping -c 1 hub
```

### Container Exits Immediately
**Error:** `Status: Exited (1)`

**Cause:** Application error during startup

**Solution:**
```bash
# Check logs
docker-compose logs worker

# Run interactively for debugging
docker run -it python:3.12-slim /bin/bash

# Check Dockerfile CMD is correct
grep "^CMD" Dockerfile
```

## Database Issues

### Database Locked
**Error:** `sqlite3.OperationalError: database is locked`

**Cause:** Multiple processes writing simultaneously

**Solution:**
```bash
# Check what has database open
lsof | grep ixpansion_resources.sqlite3

# Stop all processes
docker-compose down

# Fix database
sqlite3 ixpansion_resources.sqlite3 "PRAGMA journal_mode=WAL;"

# Restart
docker-compose up
```

### Database Corruption
**Error:** `database disk image is malformed`

**Cause:** Ungraceful shutdown or hardware failure

**Solution:**
```bash
# Backup corrupted database
cp ixpansion_resources.sqlite3 ixpansion_resources.sqlite3.bak

# Try recovery
sqlite3 ixpansion_resources.sqlite3 ".recover" | sqlite3 ixpansion_resources.sqlite3.recovered

# If recovery works
mv ixpansion_resources.sqlite3.recovered ixpansion_resources.sqlite3

# Otherwise restore from backup
cp /backup/ixpansion_resources.sqlite3.20260801 ixpansion_resources.sqlite3
```

### Out of Disk Space
**Error:** `IOError: database or disk is full`

**Cause:** Disk full or quota exceeded

**Solution:**
```bash
# Check disk usage
df -h

# Clean up old jobs
sqlite3 ixpansion_resource_jobs.sqlite3 \
  "DELETE FROM jobs WHERE status='complete' AND created_at < datetime('now', '-30 days');"

# Vacuum to reclaim space
sqlite3 ixpansion_resource_jobs.sqlite3 "VACUUM;"

# Free up space (remove old files/backups)
rm -rf old_backups/
docker system prune -a
```

## Network Issues

### TokenRouter API Timeout
**Error:** `ConnectionError: Max retries exceeded`

**Cause:** Network connectivity or API server down

**Solution:**
```bash
# Check network connectivity
curl https://api.tokenrouter.com/v1

# Verify API key
echo $TOKENROUTER_API_KEY

# Check timeout settings
# In agent.py, increase timeout
httpx.get(url, timeout=30.0)

# Fall back to offline mode
agent = Agent()  # Works offline without API key
result = agent.use_skill("extract_urls", text)
```

### Resource Collection Fails
**Error:** `HTTPError: 403 Forbidden`

**Cause:** URL not allowed or authentication required

**Solution:**
```python
from security_controls import URLPolicy

# Check allowed hosts
policy = URLPolicy({"example.com", "docs.example.com"})

# Verify URL is allowed
from urllib.parse import urlparse
host = urlparse("https://example.com/data").netloc
is_allowed = host in policy.hosts

# Add host if needed
policy.hosts.add("new-host.com")
```

## Memory Issues

### Out of Memory
**Error:** `MemoryError` or `Cannot allocate memory`

**Cause:** Large memory usage (unbounded context, memory leaks)

**Solution:**
```python
# Monitor memory usage
import tracemalloc
tracemalloc.start()

# Your code here

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024}KB; Peak: {peak / 1024}KB")

# Check agent memory limits
agent = Agent(memory_limit=1000)  # Max 1000 entries

# Clear memory periodically
agent.flush_memory()
```

## Performance Issues

### Slow Task Routing
**Error:** Task assignment takes > 1 second

**Cause:** Linear search through agents

**Solution:**
```python
# Current (O(n*m) where n=roles, m=agents per role)
for role, agents in workforce.agents.items():
    for agent in agents:
        if agent.can_perform_task(capability):
            # Found it

# Better: Cache capability -> agents mapping
agents_by_capability = defaultdict(list)
for spec in AGENT_REGISTRY.values():
    for cap in spec.skills:
        agents_by_capability[cap].append(spec.role)
```

### High CPU Usage
**Error:** CPU at 100% continuously

**Cause:** Busy-wait loops or inefficient algorithm

**Solution:**
```python
# Add sleep to prevent busy-waiting
import time

while task_pending:
    # Check status
    if task_completed:
        break
    time.sleep(0.1)  # Don't spin-wait

# Use events/callbacks instead
task.register_callback(on_complete)
# ... event-driven ...
```

## Debugging Techniques

### Add Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def my_function():
    logger.debug("Function called")
    logger.info("Processing started")
    try:
        result = operation()
        logger.info(f"Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        raise
```

### Use Python Debugger

```python
# Break at a point
breakpoint()

# In the debugger:
# n - next line
# s - step into function
# c - continue
# l - list code
# p variable - print variable
# h - help
```

### Print State

```python
# Workspace state
agent = Agent()
print(f"Memory size: {len(agent.memory)}")
print(f"Skills: {agent.list_skills()}")
print(f"Usage: {agent.usage_report()}")

# Workforce state
workforce = get_workforce()
status = workforce.report_workforce_status()
print(json.dumps(status, indent=2))
```

## When to Ask for Help

If you've tried the above and still stuck:

1. **Gather information:**
   - Full error message and traceback
   - Python version (`python --version`)
   - Environment (`echo $PYTHONPATH`)
   - Reproduction steps

2. **Check documentation:**
   - README.md - Architecture
   - AGENTS.md - Agent reference
   - API.md - Endpoint reference
   - DEVELOPMENT.md - Development guide

3. **Search issues:**
   - GitHub Issues for your error message
   - StackOverflow for the specific error type

4. **Open an issue with:**
   - Clear title: "Cannot import agent module"
   - Description: What you did, what happened
   - Environment: Python 3.12, Ubuntu 22.04, etc.
   - Steps to reproduce: Exact commands
   - Expected vs. actual behavior

---

**Note:** Most issues have simple fixes. Check the relevant section above or run `make verify` to validate your setup.
