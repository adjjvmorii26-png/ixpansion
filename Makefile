.PHONY: verify test compile swarm-config

compile:
	python -m py_compile agent.py run_agent.py run_1_3_stack.py tokenrouter_client.py xai_client.py api/main.py aether_lattice.py security_controls.py federated_stack.py lattice_stack.py

test:
	python -m unittest discover -s tests -v

verify: compile test

swarm-config:
	docker compose config