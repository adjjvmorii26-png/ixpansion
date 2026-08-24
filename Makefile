.PHONY: test test-nexus test-projects test-solid-organism test-ixpansion test-prime test-fractal test-root test-bridges test-mycelium test-lab test-constellation mandate-dry mandate-run genome-list genome-atlas lint clean backup push

test:
	python3 -m pytest -q --tb=short

test-nexus:
	python3 -m pytest nexus_observatory/tests -q --tb=short

test-projects:
	python3 -m pytest projects/tests -q --tb=short

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

test-lab:
	python3 -m pytest lab/tests -q --tb=short

test-constellation:
	python3 -m pytest constellation/tests -q --tb=short

mandate-dry:
	python3 lab/pulse_oracle.py
	python3 lab/ritual_parliament.py
	python3 lab/reversible_mandate.py --dry-run
	python3 bridges/mandate_resonance.py

mandate-run:
	python3 lab/pulse_oracle.py
	python3 lab/ritual_parliament.py
	python3 lab/reversible_mandate.py
	python3 bridges/mandate_resonance.py
	python3 lab/mandate_genome.py forge

genome-list:
	python3 lab/mandate_genome.py list

genome-atlas:
	python3 lab/genome_observatory.py census
	python3 lab/genome_observatory.py atlas

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
