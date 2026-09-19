.PHONY: test test-full lint clean backup push

test:
	python3 -m pytest tests/ -q --tb=short -n auto --dist loadgroup

test-full:
	python3 -m pytest tests/ -v --tb=short

lint:
	@find . -type f -name '*.py' \
		! -path './backup/*' ! -path '*/__pycache__/*' -print0 | \
		xargs -0 -n1 python3 -m py_compile
	@echo "All Python files compile."

clean:
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	@rm -rf .pytest_cache omega_fractal_engine/.pytest_cache

backup:
	@mkdir -p backup
	@tar czf "backup/aleph-$$(date -u +%Y%m%d-%H%M%S).tgz" \
		--exclude='.git' --exclude='__pycache__' --exclude='.pytest_cache' \
		--exclude='*.pyc' --exclude='backup' .
	@echo "Backup created."

push: test lint
	git add -A && git commit -m "refine: automated commit" || echo "nothing to commit"
	git push origin main

cli:
	python3 cli.py status

monitor:
	python3 monitor.py

health:
	python3 cli.py health

benchmark:
	python3 cli.py benchmark

fast-gate:
	python3 -m pytest tests/test_wave432.py tests/test_wave433.py tests/test_wave434.py tests/test_wave435.py tests/test_wave436.py tests/test_wave437.py tests/test_wave438.py tests/test_wave439.py tests/test_wave440.py -q --tb=short -x

# ─── Coolify targets ───
coolify-build:
	docker compose build

coolify-up:
	docker compose up -d

coolify-down:
	docker compose down

coolify-logs:
	docker compose logs -f ixpansion

coolify-restart:
	docker compose restart

coolify-health:
	@curl -sf http://localhost:3000/health && echo "\n  Organism is alive ✓" || echo "\n  Organism is down ✗"

coolify-status:
	@docker compose ps

coolify-image:
	docker build -t ghcr.io/adjjvmorii26-png/ixpansion:latest .
	docker push ghcr.io/adjjvmorii26-png/ixpansion:latest

coolify-clean:
	docker compose down -v
	docker rmi ghcr.io/adjjvmorii26-png/ixpansion:latest 2>/dev/null || true

# ─── Stable terminal ───
.PHONY: shell council env-check dashboard snapshot

shell:
	@bash scripts/ix_shell.sh

council:
	@PYTHONPATH=. python3 lab/ops/copilots/council.py

env-check:
	@echo "ROOT=$$(pwd)"
	@echo "PY=$$(command -v python3)"
	@test -f lab/ops/copilots/council.py && echo "council: ok" || echo "council: missing (git pull origin main)"
	@git rev-parse --abbrev-ref HEAD 2>/dev/null || true

dashboard:
	@PYTHONPATH=. python3 lab/ops/dashboard_server.py --host 127.0.0.1 --port 8765

snapshot:
	@PYTHONPATH=. python3 lab/ops/status_snapshot.py
