# IXPANSION — Coolify / Docker image
# Runs the full organism via api_server.py (stdlib-only, no external deps).
FROM python:3.11-slim

LABEL org.opencontainers.image.title="IXPANSION"
LABEL org.opencontainers.image.description="Self-evolving computational organism"
LABEL org.opencontainers.image.version="4.97.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    API_HOST=0.0.0.0 \
    API_PORT=3000

WORKDIR /app

# Copy entire organism (api, data, dashboard, tests, configs)
COPY api/ /app/api/
COPY data/ /app/data/
COPY dashboard/ /app/dashboard/
COPY tests/ /app/tests/
COPY cli.py api_server.py main.py index.html *.md *.toml *.cff Makefile /app/

EXPOSE 3000

# Healthcheck against the organism health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/health', timeout=4)" || exit 1

CMD ["python3", "api_server.py", "--port", "3000", "--host", "0.0.0.0"]
