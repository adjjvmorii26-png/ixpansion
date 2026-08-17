# IXPANSION CI/CD & Deployment

Continuous integration, testing, and deployment guide for IXPANSION.

## Overview

The repository uses GitHub Actions for CI/CD with:
- Automated test execution on every push
- Code quality checks
- Docker image building
- Release automation

## GitHub Actions Workflows

### Workflow Location
`.github/workflows/ci.yml` - Main CI pipeline

### CI Pipeline Stages

#### 1. Code Quality Checks
```yaml
- Lint Python code
- Check type hints
- Verify imports
- Validate JSON/YAML
```

#### 2. Unit Testing
```yaml
- Run all unit tests
- Generate coverage report
- Verify coverage thresholds
- Test on Python 3.12
```

#### 3. Integration Testing
```yaml
- Test API endpoints
- Test CLI commands
- Verify Docker image
- Test compose configuration
```

#### 4. Security Scanning
```yaml
- Scan for secrets
- Check dependencies for vulnerabilities
- Verify no credentials in examples
- Audit imports
```

#### 5. Build & Release (on tag)
```yaml
- Build Docker image
- Push to registry
- Create GitHub release
- Update version in files
```

## Local Pre-Commit Testing

Run before committing:

```bash
# Full verification
make verify

# Specific checks
make compile           # Syntax validation
make test             # Unit tests
make workforce-test   # Workforce tests
```

## Docker Image

### Building Locally

```bash
# Build image
docker build -t ixpansion:latest .

# Run container
docker run -p 8000:8000 ixpansion:latest

# Run swarm demo
docker-compose up
```

### Image Contents

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONUNBUFFERED=1

CMD ["python", "swarm_runtime.py"]
```

### Image Optimization

- **Base:** `python:3.12-slim` (100MB)
- **Dependencies:** Pinned versions
- **Size:** ~400MB total
- **Layers:** Multi-stage build not needed (Python app)

## Environment Configuration

### Development (.env.example)
```bash
# TokenRouter API (optional for premium models)
TOKENROUTER_API_KEY=your_key_here
TOKENROUTER_MODEL=openai/gpt-4.1
TOKENROUTER_API_URL=https://api.tokenrouter.com/v1
```

### Production
```bash
# Resource management
IXPANSION_RESOURCE_HOSTS=api.example.com,data.example.com
IXPANSION_RESOURCE_WORKERS=4
IXPANSION_RESOURCE_MAX_PENDING=50

# Database
IXPANSION_RESOURCE_DB=/var/lib/ixpansion/resources.db
IXPANSION_RESOURCE_JOBS_DB=/var/lib/ixpansion/jobs.db

# Swarm security
SWARM_TOKEN=secure_token_here

# Optional: Premium models
TOKENROUTER_API_KEY=sk-...
XAI_API_KEY=xai-...
```

## Deployment Scenarios

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run API
python -m uvicorn api.main:app --reload --port 8000

# Run CLI
python run_agent.py --goal "Your goal"

# Run swarm demo
docker-compose up
```

### Single Container

```bash
# Build
docker build -t myregistry/ixpansion:1.0.0 .

# Push
docker push myregistry/ixpansion:1.0.0

# Run
docker run \
  -p 8000:8000 \
  -e SWARM_TOKEN=token \
  myregistry/ixpansion:1.0.0
```

### Docker Compose (Local Swarm)

```bash
# Start full stack
docker-compose up -d

# Monitor
docker-compose logs -f

# Scale workers
docker-compose up -d --scale worker=3

# Cleanup
docker-compose down
```

### Kubernetes

Create deployment manifests:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ixpansion-config
data:
  SWARM_ROLE: "hub"
  IXPANSION_RESOURCE_WORKERS: "4"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ixpansion-hub
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ixpansion
      role: hub
  template:
    metadata:
      labels:
        app: ixpansion
        role: hub
    spec:
      containers:
      - name: hub
        image: myregistry/ixpansion:latest
        ports:
        - containerPort: 8765
        envFrom:
        - configMapRef:
            name: ixpansion-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8765
          initialDelaySeconds: 10
          periodSeconds: 10
```

## Version Management

### Versioning Scheme
Semantic versioning: `MAJOR.MINOR.PATCH-PRERELEASE`

Examples:
- `1.0.0` - Initial release
- `1.1.0` - New features, backward compatible
- `1.1.1` - Bug fixes
- `1.2.0-rc1` - Release candidate
- `2.0.0` - Breaking changes

### Version Location

Update in:
1. `api/main.py` - `app = FastAPI(version="X.Y.Z")`
2. Git tag - `git tag vX.Y.Z`
3. Release notes - `.github/releases/`

### Release Checklist

```bash
# 1. Update version in code
# 2. Update CHANGELOG
# 3. Commit
git commit -m "chore: release v1.2.0"

# 4. Tag
git tag v1.2.0

# 5. Push
git push origin main
git push origin v1.2.0

# 6. Create release on GitHub (auto-triggered)
# 7. Build and push Docker image (auto-triggered)
```

## Monitoring & Observability

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Aether status
curl http://localhost:8000/aether/status

# Lattice status
curl http://localhost:8000/lattice/status
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Agent started", extra={"agent_name": "aether"})
```

### Metrics Collection

Key metrics to track:
- Agent skill usage frequency
- Task completion rate
- Lattice machine health
- Trust score trends
- Resource collection success rate
- API response times

### Alerts (Production)

Set up alerts for:
- API down (health check fails)
- High error rate (>5% of requests)
- Skill timeouts
- Machine health degradation
- Disk space running low
- Database connection issues

## Rollback Procedures

### Container Rollback

```bash
# List available versions
docker image ls | grep ixpansion

# Stop current
docker-compose down

# Revert to previous version
export IMAGE_TAG=v1.1.0
docker-compose up -d
```

### Code Rollback

```bash
# Identify problematic commit
git log --oneline

# Revert
git revert <commit-hash>
git push origin main

# Or reset (force, not recommended)
git reset --hard <safe-commit>
git push --force origin main
```

## Backup & Disaster Recovery

### Backup Strategy

```bash
# Backup databases
mkdir -p backups
sqlite3 ixpansion_resources.sqlite3 ".backup backups/resources_$(date +%Y%m%d).db"
sqlite3 ixpansion_resource_jobs.sqlite3 ".backup backups/jobs_$(date +%Y%m%d).db"

# Backup to S3 (example)
aws s3 sync backups/ s3://my-backup-bucket/ixpansion/
```

### Recovery Procedures

```bash
# Restore from backup
sqlite3 ixpansion_resources.sqlite3 < backups/resources_20260817.db

# Verify integrity
sqlite3 ixpansion_resources.sqlite3 "PRAGMA integrity_check;"

# Restart service
docker-compose restart api
```

## Performance Tuning

### Database Optimization

```sql
-- Create indices for frequently queried columns
CREATE INDEX idx_resources_url ON resources(source_url);
CREATE INDEX idx_jobs_status ON resource_jobs(status);
CREATE INDEX idx_jobs_created ON resource_jobs(created_at);

-- Regular cleanup
DELETE FROM resource_jobs WHERE status='failed' AND created_at < datetime('now', '-7 days');
VACUUM;  -- Reclaim space
```

### API Performance

```python
# Add caching headers
response.headers["Cache-Control"] = "public, max-age=3600"

# Gzip compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Worker Pool Tuning

```bash
# Set optimal worker count
# Recommendation: 2 * CPU_CORES

export IXPANSION_RESOURCE_WORKERS=8  # For 4-core system
```

## Security Hardening

### HTTPS in Production

```bash
# Generate SSL certificate
certbot certonly --standalone -d ixpansion.example.com

# Configure HTTPS
export SSL_CERT=/etc/letsencrypt/live/ixpansion.example.com/fullchain.pem
export SSL_KEY=/etc/letsencrypt/live/ixpansion.example.com/privkey.pem

# Run with HTTPS
uvicorn api.main:app --ssl-keyfile=$SSL_KEY --ssl-certfile=$SSL_CERT
```

### Network Security

```yaml
# Docker network isolation
services:
  api:
    networks:
      - internal
    expose:
      - 8000
  
  hub:
    networks:
      - internal
    expose:
      - 8765

networks:
  internal:
    driver: bridge
```

### Secrets Management

```bash
# Never commit secrets
git log --name-only | xargs grep -l "password\|key\|secret" 2>/dev/null

# Use environment variables
export TOKENROUTER_API_KEY=$(aws secretsmanager get-secret-value --secret-id ixpansion/api-key | jq -r .SecretString)

# Or use secret management tools:
# - AWS Secrets Manager
# - HashiCorp Vault
# - Kubernetes Secrets
```

## Troubleshooting

### Build Failures

```bash
# Clear Docker cache
docker-compose build --no-cache

# Check Python version
python --version  # Must be 3.12+

# Reinstall dependencies
pip install --upgrade --force-reinstall -r requirements.txt
```

### Test Failures

```bash
# Run with verbose output
python -m unittest discover -s tests -v

# Show full traceback
python -m pytest tests/ -vv --tb=long
```

### Runtime Issues

```bash
# Check logs
docker-compose logs -f api

# Check resource usage
docker stats

# Inspect containers
docker ps -a
docker inspect <container-id>
```

## See Also

- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide
- [README.md](README.md) - Architecture overview
- [.github/workflows/ci.yml](.github/workflows/ci.yml) - CI configuration
- [docker-compose.yml](docker-compose.yml) - Local swarm demo
- [Dockerfile](Dockerfile) - Container image
