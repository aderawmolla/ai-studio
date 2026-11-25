.PHONY: film test status logs install

# Default: full pipeline (storyboard as-is)
# Named film with real AI:
#   make film ARGS='--real --fresh "Rock-hewn churches of Lalibela" lalibela.mp4'
film:
	python3 run_film.py $(ARGS)

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

test:
	.venv/bin/pytest -q

status:
	python3 main.py status

logs:
	python3 main.py logs -n 50