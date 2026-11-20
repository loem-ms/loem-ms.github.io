# Build, check and preview the site locally. `make setup` once, then `make check` before every PR.
PY := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
PORT ?= 8765

.PHONY: setup build check serve

setup:            ## create .venv with the builders' dependencies
	python3 -m venv .venv
	.venv/bin/pip install -q -r requirements-notes.txt

build:            ## regenerate every page from content/ (order matters: site reads the manifests)
	$(PY) scripts/build_notes.py
	$(PY) scripts/build_projects.py
	$(PY) scripts/build_site.py

check: build      ## build, then check links, titles and image alt text in the generated pages
	$(PY) scripts/check_site.py

serve:            ## preview at http://localhost:$(PORT)/
	$(PY) -m http.server $(PORT) --bind 127.0.0.1
