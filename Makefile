# Heritage Short — use .venv Python for every target (run `make install` first).

PYTHON := .venv/bin/python3
PIP    := .venv/bin/pip

.PHONY: install help film test status logs doctor
.PHONY: validate story references images videos
.PHONY: narration music subtitles audio validate-media assemble final-check generate

install:
	python3 -m venv .venv
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt
	@echo ""
	@echo "Done. Activate the venv when using python3 directly:"
	@echo "  source .venv/bin/activate"

help:
	@echo "Setup (once):     make install"
	@echo "Full film:        make film"
	@echo "                  make film ARGS='--real'"
	@echo "Single stages:    make assemble | make audio | make music | make narration | ..."
	@echo "                  make images | make videos | make validate | make final-check"
	@echo "Inspect:          make status | make logs | make doctor | make test"

film:
	$(PYTHON) run_film.py $(ARGS)

test:
	$(PYTHON) -m pytest -q

status:
	$(PYTHON) main.py status

logs:
	$(PYTHON) main.py logs -n 50

doctor:
	$(PYTHON) main.py doctor

validate:
	$(PYTHON) main.py validate

story:
	$(PYTHON) main.py story

references:
	$(PYTHON) main.py references

images:
	$(PYTHON) main.py images

videos:
	$(PYTHON) main.py videos

narration:
	$(PYTHON) main.py narration

music:
	$(PYTHON) main.py music

subtitles:
	$(PYTHON) main.py subtitles

audio:
	$(PYTHON) main.py audio

validate-media:
	$(PYTHON) main.py validate-media

assemble:
	$(PYTHON) main.py assemble

final-check:
	$(PYTHON) main.py final-check

generate:
	$(PYTHON) main.py generate $(if $(FROM),--from-stage $(FROM),)