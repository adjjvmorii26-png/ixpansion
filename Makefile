.PHONY: verify test compile swarm-config workforce-test workforce-lint

compile:
	python -m py_compile agent.py run_agent.py run_1_3_stack.py tokenrouter_client.py xai_client.py api/main.py aether_lattice.py security_controls.py federated_stack.py lattice_stack.py resource_store.py resource_jobs.py web_resources.py agents.py workforce.py mission_director.py

test:
	python -m unittest discover -s tests -v

workforce-test:
	python -m unittest tests.test_workforce -v

workforce-lint:
	python -m py_compile agents.py workforce.py mission_director.py

verify: compile test

swarm-config:
	docker compose config

workforce-status:
	python -c "from workforce import get_workforce; import json; w = get_workforce(); print(json.dumps(w.report_workforce_status(), indent=2))"