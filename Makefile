# Heritage Short — use .venv Python for every target (run `make install` first).
# Stage targets follow core/pipeline.py STAGE_ORDER (make film runs all of them).

PYTHON := .venv/bin/python3
PIP    := .venv/bin/pip

.PHONY: install help film test status logs doctor generate
.PHONY: validate story references images videos
.PHONY: narration music subtitles end-card validate-media assemble final-check audio

install:
	python3 -m venv .venv
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt
	@echo ""
	@echo "Done. Activate the venv when using python3 directly:"
	@echo "  source .venv/bin/activate"

help:
	@echo "Setup (once):     make install"
	@echo "Full pipeline:    make film"
	@echo "                  make film ARGS='--real'"
	@echo ""
	@echo "Stages (same order as make film):"
	@echo "  make validate"
	@echo "  make references  make images  make videos"
	@echo "  make narration   make music    make subtitles"
	@echo "  make end-card"
	@echo "  make validate-media"
	@echo "  make assemble"
	@echo "  make final-check"
	@echo ""
	@echo "Bundles:          make audio  (narration + music + subtitles)"
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

generate:
	$(PYTHON) main.py generate $(if $(FROM),--from-stage $(FROM),)

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

end-card:
	$(PYTHON) main.py end-card

validate-media:
	$(PYTHON) main.py validate-media

assemble:
	$(PYTHON) main.py assemble

final-check:
	$(PYTHON) main.py final-check

audio:
	$(PYTHON) main.py audio