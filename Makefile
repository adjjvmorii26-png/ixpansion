.PHONY: test test-prime test-fractal lint clean backup push

test:
	python3 -m pytest omega_prime/tests/ omega_fractal_engine/tests/ -v --tb=short

test-prime:
	python3 -m pytest omega_prime/tests/ -v --tb=short

test-fractal:
	python3 -m pytest omega_fractal_engine/tests/ -v --tb=short

lint:
	find . -name '*.py' ! -path './backup/*' ! -path '*__pycache__*' | while read f; do \
		python3 -m py_compile "$$f"; \
	done; echo "All files compile."

clean:
	find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache omega_fractal_engine/.pytest_cache

backup:
	tar czf backup/aleph-$$(date +%Y%m%d-%H%M%S).tgz --exclude='__pycache__' --exclude='.pytest_cache' --exclude='*.pyc' --exclude='backup' .

push: test lint
	git add -A && git commit -m "refine: automated commit" || echo "nothing to commit"
	git push origin main
