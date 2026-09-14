# Coolify Deployment Guide — IXPANSION

Coolify is a self-hosted PaaS that can deploy, manage, and auto-scale
the IXPANSION organism on any VPS or local machine.

## Quick Start (Self-Hosted Coolify)

### 1. Install Coolify on your server

```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

Then open `http://YOUR_SERVER_IP:8000` to access the Coolify dashboard.

### 2. Connect Your GitHub Repo

1. In Coolify → **Sources** → add GitHub repo: `adjjvmorii26-png/ixpansion`
2. Select branch: `main`
3. Coolify auto-detects the `Dockerfile` and `docker-compose.yml`

### 3. Deploy

1. Go to **Applications** → **New Application**
2. Choose **Docker Compose** deployment method
3. Coolify reads `docker-compose.yml` from the repo root
4. Set environment variables (or use defaults):
   - `API_PORT=3000`
   - `NEXUS_MODE=production`
5. Click **Deploy**

### 4. Configure Domain (Optional)

1. In Coolify → **Networking** → add your domain
2. Enable **Let's Encrypt** for automatic SSL
3. The organism is now live at `https://your-domain.com`

---

## Deployment Options

### Option A: Docker Compose (Recommended)
- Uses the existing `docker-compose.yml`
- Coolify manages build, healthchecks, restarts
- Persistent data via `ixpansion_data` volume

### Option B: Dockerfile Only
- Coolify builds from `Dockerfile` directly
- Less control over volumes/compose features

### Option C: Pre-built Image
- Push image to `ghcr.io/adjjvmorii26-png/ixpansion:latest`
- Coolify pulls and deploys directly
- Fastest deploy, no build step

---

## Coolify Settings

| Setting | Value |
|---------|-------|
| Port | 3000 |
| Health Check | `/health` |
| Interval | 30s |
| Timeout | 5s |
| CPU | 1 core |
| Memory | 512MB |
| Volume | `ixpansion_data` → `/app/data` |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_PORT` | 3000 | Server port |
| `API_HOST` | 0.0.0.0 | Bind address |
| `NEXUS_MODE` | production | Runtime mode |
| `NEXUS_SEED` | 42 | Random seed |
| `API_KEY` | (set manually) | API access key |

---

## Auto-Deploy from GitHub

Coolify can auto-deploy on every push to `main`:

1. In Coolify → **Source** → enable **Auto Deploy**
2. Every `git push origin main` triggers a rebuild
3. Organism evolves automatically across deploys

---

## Monitoring

### Coolify Dashboard
- Real-time container logs
- Resource usage (CPU, RAM, network)
- Deployment history
- Health status

### Organism Dashboard
- All dashboards live at `https://your-domain.com/dashboard/`
- Key dashboards:
  - `/dashboard/` — main hub
  - `/dashboard/meta-regulation.html` — genome & modes
  - `/dashboard/temporal-field.html` — module age
  - `/dashboard/coherence-gradient.html` — coherence flow

---

## Coolify CLI Commands

```bash
# Install Coolify
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# Manage via Coolify API
curl -X GET https://YOUR_COOLIFY_URL/api/v1/applications \
  -H "Authorization: Bearer YOUR_COOLIFY_TOKEN"

# Deploy via API
curl -X POST https://YOUR_COOLIFY_URL/api/v1/applications/APP_ID/deploy
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Container won't start | Check logs in Coolify → Logs tab |
| Health check fails | Verify `/health` endpoint returns 200 |
| Port conflict | Change `API_PORT` in environment |
| Data not persisting | Ensure `ixpansion_data` volume is mounted |
| Build fails | Check `.dockerignore` includes all needed dirs |
