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
