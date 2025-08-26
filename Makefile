.PHONY: run install-dependencies create-venv

create-venv:
	@python3 -m venv .venv

install-dependencies:
	@pip install -r requirements.txt

run:
	@python3 src/main.py
