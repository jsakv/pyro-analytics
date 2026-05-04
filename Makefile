SPHINXOPTS ?=
SPHINXBUILD ?= uv run --group docs sphinx-build
SPHINXAPIDOC ?= uv run --group docs sphinx-apidoc
SPHINXAPIDOCOPTS ?= -f -e -M -T --remove-old --automodule-options members,undoc-members,show-inheritance,ignore-module-all
SOURCEDIR = docs
BUILDDIR = docs/_build
PYTHON ?= uv run python
DOCS_PORT ?= 8000

.PHONY: setup install sync install-hooks format lint type test test-cov html build-docs docs serve-docs check

setup: sync install-hooks

install: setup

sync:
	uv sync

install-hooks:
	uv run pre-commit install

format:
	uv run ruff format .

lint:
	uv run ruff check .

type:
	uv run mypy

test:
	uv run pytest

test-cov:
	uv run pytest --cov=analytics --cov=packages

html:
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

docs:
	$(MAKE) build-docs

build-docs:
	$(SPHINXAPIDOC) $(SPHINXAPIDOCOPTS) -o "$(SOURCEDIR)/reference/analytics" src/analytics
	$(SPHINXAPIDOC) $(SPHINXAPIDOCOPTS) -o "$(SOURCEDIR)/reference/sources" packages/sources/src/sources
	$(SPHINXAPIDOC) $(SPHINXAPIDOCOPTS) -o "$(SOURCEDIR)/reference/pyromap" packages/pyromap/src/pyromap
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" -W --keep-going $(SPHINXOPTS) $(O)

serve-docs: html
	$(PYTHON) -m http.server $(DOCS_PORT) --directory "$(BUILDDIR)/html"

check:
	uv run ruff format . --check
	uv run ruff check .
	uv run mypy
	uv run pytest
