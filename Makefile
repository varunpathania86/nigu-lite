# nigu-lite — the Makefile is the only entry point (AGENTS.md).
# Complex logic lives in scripts/ or <product>/scripts/; targets stay one or two lines.

SHELL := /bin/bash
.DEFAULT_GOAL := help
MISE ?= $(shell command -v mise 2>/dev/null || echo $(HOME)/.local/bin/mise)
# Pinned tools from .tool-versions, even in a terminal opened before make setup
RUN := $(MISE) exec --
PYTHON := $(RUN) python

.PHONY: help setup doctor lint test-unit scan check-docs fix-docs

help: ## List targets
	@grep -hE '^[a-z0-9-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

setup: ## Install everything a developer machine needs (idempotent)
	bash scripts/setup/setup.sh

doctor: ## Check the developer machine without changing it
	bash scripts/setup/setup.sh --check

lint: ## Run all pre-commit hooks on all files
	$(RUN) pre-commit run --all-files --show-diff-on-failure

test-unit: ## Run unit tests
	$(PYTHON) -m unittest discover --start-directory tests/unit --top-level-directory . --verbose

scan: ## Trivy filesystem scan: secrets, misconfiguration, vulnerabilities
	$(RUN) trivy fs --scanners secret,misconfig,vuln --exit-code 1 --severity HIGH,CRITICAL --skip-dirs .git .

check-docs: ## Check AGENTS index, instruction sizes, templates and mermaid blocks
	$(PYTHON) scripts/check_docs.py

fix-docs: ## Copy mermaid classDef/subgraph styles from docs/diagram-style.md into every diagram, then check
	$(PYTHON) scripts/check_docs.py --fix
