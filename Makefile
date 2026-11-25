.PHONY: film test status logs install

# One command for the assignment README (full pipeline)
film:
	python3 run_film.py

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

test:
	.venv/bin/pytest -q

status:
	python3 main.py status

logs:
	python3 main.py logs -n 50