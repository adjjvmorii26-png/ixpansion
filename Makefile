.PHONY: test test-solid-organism test-ixpansion test-prime test-fractal test-root test-bridges test-mycelium lint clean backup push

test:
	python3 -m pytest -q --tb=short

test-solid-organism:
	python3 -m pytest solid-organism/tests -q --tb=short

test-ixpansion:
	python3 -m pytest ixpansion/tests -q --tb=short

test-prime:
	python3 -m pytest omega_prime/tests -q --tb=short

test-fractal:
	python3 -m pytest omega_fractal_engine/tests -q --tb=short

test-root:
	python3 -m pytest project_root/tests -q --tb=short

test-bridges:
	python3 -m pytest bridges -q --tb=short

test-mycelium:
	python3 -m pytest mycelium/tests -q --tb=short

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
