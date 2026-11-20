# nigu-lite — the Makefile is the only entry point (AGENTS.md).
# Complex logic lives in scripts/ or <product>/scripts/; targets stay one or two lines.

SHELL := /bin/bash
.DEFAULT_GOAL := help
MISE ?= mise
# Pinned tools from .tool-versions, even when mise is not activated in the shell
RUN := $(MISE) exec --
PYTHON := $(RUN) python

.PHONY: help setup lint test-unit scan check-docs

help: ## List targets
	@grep -hE '^[a-z0-9-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

setup: ## Install pinned tools (mise) and git hooks
	$(MISE) install
	$(RUN) pre-commit install --install-hooks --hook-type pre-commit --hook-type commit-msg

lint: ## Run all pre-commit hooks on all files
	$(RUN) pre-commit run --all-files --show-diff-on-failure

test-unit: ## Run unit tests
	$(PYTHON) -m unittest discover --start-directory tests/unit --top-level-directory . --verbose

scan: ## Trivy filesystem scan: secrets, misconfiguration, vulnerabilities
	$(RUN) trivy fs --scanners secret,misconfig,vuln --exit-code 1 --severity HIGH,CRITICAL --skip-dirs .git .

check-docs: ## Check AGENTS index, instruction sizes, templates and mermaid blocks
	$(PYTHON) scripts/check_docs.py
