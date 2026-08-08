.PHONY: verify test compile

compile:
	python -m py_compile agent.py run_agent.py tokenrouter_client.py xai_client.py api/main.py security_controls.py

test:
	python -m unittest discover -s tests -v

verify: compile test