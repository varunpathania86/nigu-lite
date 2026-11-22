# nigu-lite — the Makefile is the only entry point (AGENTS.md).
# Complex logic lives in scripts/ or <product>/scripts/; targets stay one or two lines.

SHELL := /bin/bash
.DEFAULT_GOAL := help
export PYTHONPATH := $(CURDIR)
MISE ?= $(shell command -v mise 2>/dev/null || echo $(HOME)/.local/bin/mise)
# Pinned tools from .tool-versions, even in a terminal opened before make setup
ifeq ($(NIGU_BUILD_CONTAINER),1)
RUN :=
PYTHON := /opt/nigu-ci/bin/python
else
RUN := $(MISE) exec --
PYTHON := $(MISE) exec python@3.14.10 -- python
endif
OUT_DIR ?= report
MODE ?= worktree
NIGU_REGISTRY_PORT ?= 5000
HOST_PYTHON ?= python3

.PHONY: help setup doctor lint test-unit scan check-docs fix-docs \
	manifest-validate ci-catalog ci-plan ci-quality ci-test-unit ci-scan ci-module ci-reviewdog ci-report \
	ci-security-reports ci-allure ci-pages-index ci-report-dir ci-pages-configure \
	act-build act-iac act-publish registry-up registry-status registry-down deploy tenant-package image-build

help: ## List targets
	@grep -hE '^[a-z0-9-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

setup: ## Install everything a developer machine needs (idempotent)
	bash scripts/setup/setup.sh

doctor: ## Check the developer machine without changing it
	bash scripts/setup/setup.sh --check

lint: ## Run lint in an ephemeral Build Container
ifeq ($(NIGU_BUILD_CONTAINER),1)
	$(RUN) pre-commit run --all-files --show-diff-on-failure
else
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-lint
endif

test-unit: ## Run unit tests in an ephemeral Build Container
ifeq ($(NIGU_BUILD_CONTAINER),1)
	$(PYTHON) -m unittest discover --start-directory tests/unit --top-level-directory . --verbose
else
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-test-unit
endif

scan: ## Run Trivy in an ephemeral Build Container
ifeq ($(NIGU_BUILD_CONTAINER),1)
	trivy fs --scanners secret,misconfig,vuln --exit-code 1 --severity HIGH,CRITICAL --skip-dirs .git .
else
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-scan
endif

check-docs: ## Check AGENTS index, instruction sizes, templates and mermaid blocks
	$(PYTHON) scripts/check_docs.py

fix-docs: ## Copy mermaid classDef/subgraph styles from docs/diagram-style.md into every diagram, then check
	$(PYTHON) scripts/check_docs.py --fix

manifest-validate: ## Validate schemas in an ephemeral Build Container
ifeq ($(NIGU_BUILD_CONTAINER),1)
	$(PYTHON) scripts/manifests/validator.py --root . --output $(OUT_DIR)/manifest-validation.json
else
	MODE=$(MODE) bash scripts/act/run-build-container.sh manifest-validate
endif

ci-lint: ## Internal Build Container lint target
	$(PYTHON) scripts/ci/job.py --job lint --output $(OUT_DIR)/parts/lint.json -- \
		pre-commit run --all-files --show-diff-on-failure

ci-test-unit: ## Internal Build Container unit-test target
	$(PYTHON) scripts/ci/job.py --job unit --output $(OUT_DIR)/parts/unit.json -- \
		$(PYTHON) -m unittest discover --start-directory tests/unit --top-level-directory . --verbose

ci-scan: ## Internal Build Container Trivy target
	@status=0; \
	trivy fs --scanners secret,misconfig,vuln --skip-db-update --skip-check-update \
		--ignore-unfixed --exit-code 1 --severity HIGH,CRITICAL \
		--format json --output $(OUT_DIR)/trivy-report.json --skip-dirs .git . || status=$$?; \
	trivy convert --format sarif --output $(OUT_DIR)/trivy.sarif $(OUT_DIR)/trivy-report.json; \
	ruff check --exit-zero --output-format=sarif --output-file $(OUT_DIR)/ruff.sarif .; \
	$(PYTHON) scripts/ci/job.py --job scan --output $(OUT_DIR)/parts/scan.json \
		--record-exit-code $$status --summary "Trivy filesystem, configuration and secret scan"; \
	exit $$status

ci-catalog: ## Validate and inventory CI modules
	$(PYTHON) scripts/ci/catalog.py --root . --output $(OUT_DIR)/catalog.json

ci-plan: ## Plan changed modules from a commit or explicit paths file
	$(PYTHON) scripts/ci/plan.py --catalog $(OUT_DIR)/catalog.json --base $(BASE) \
		$(if $(PATHS_FILE),--paths-file $(PATHS_FILE),) --modules "$(MODULES)" \
		$(if $(GITHUB_OUTPUT),--github-output $(GITHUB_OUTPUT),) > $(OUT_DIR)/plan.json

ci-module: ci-catalog ## Build or package one catalog module
	$(PYTHON) scripts/ci/module.py --catalog $(OUT_DIR)/catalog.json --id "$(ID)" --output $(OUT_DIR)/modules

ci-quality: ## Run the blocking quality leg inside a Build Container
	$(MAKE) ci-lint ci-test-unit ci-scan ci-catalog

ci-render: ## Render synthetic policy inputs
	$(PYTHON) scripts/ci/render.py --root . --output $(OUT_DIR)/rendered

ci-iac: ## Run rendered advisory KICS, conftest and Trivy config checks
	$(MAKE) ci-catalog ci-render
	trivy config --format json --output $(OUT_DIR)/trivy-config.json $(OUT_DIR)/rendered
	conftest test --no-fail --policy policy/iac $(OUT_DIR)/rendered/*.json
	docker run --rm --volume "$(NIGU_HOST_OUTPUT)/rendered:/path" \
		checkmarx/kics:v2.2.1@sha256:49ccc54b6ae7f5d5fc95e96f8f95c18c57f3bba047ab611a03d80792bdff6757 \
		scan -p /path -o /path/kics-results --report-formats json --ignore-on-exit results

ci-publish: ## Publish planned artifacts to an explicitly selected registry
	test -n "$(REGISTRY)" || (echo "REGISTRY is required" >&2; exit 2)
	$(MAKE) ci-catalog ci-plan
	$(PYTHON) scripts/ci/publish.py --plan $(OUT_DIR)/plan.json --registry "$(REGISTRY)" \
		--root . --output $(OUT_DIR)/publish $(if $(filter 1,$(LOCAL)),--local,)

ci-retention: ## Generate a safe retention plan
	$(PYTHON) scripts/ci/retention.py $(if $(METADATA),--metadata $(METADATA),) \
		--output $(OUT_DIR)/retention.json $(if $(filter 1,$(APPLY)),--apply,)

ci-release: ## Create a tag release from trusted publish evidence
	$(PYTHON) scripts/ci/release.py --publish-dir $(OUT_DIR)/publish \
		--output $(OUT_DIR)/release.json

ci-plan-output: ## Export a plan to GitHub Actions output
	$(PYTHON) scripts/ci/github_output.py --plan $(OUT_DIR)/plan.json --output "$(GITHUB_OUTPUT)"

ci-reviewdog: ## Publish Trivy and Ruff SARIF as PR checks and comments
	reviewdog -f=sarif -name=Trivy -reporter=github-pr-review \
		-filter-mode=added -level=warning -fail-level=none < "$(SARIF)"
	reviewdog -f=sarif -name=Trivy -reporter=github-pr-check \
		-filter-mode=added -level=warning -fail-level=none < "$(SARIF)"
	reviewdog -f=sarif -name=Ruff -reporter=github-pr-review \
		-filter-mode=added -level=warning -fail-level=none < "$(LINT_SARIF)"
	reviewdog -f=sarif -name=Ruff -reporter=github-pr-check \
		-filter-mode=added -level=warning -fail-level=none < "$(LINT_SARIF)"

ci-security-reports: ## Generate static security and SBOM reports
	mkdir -p $(OUT_DIR)/public/security $(OUT_DIR)/public/sbom
	trivy fs --scanners secret,misconfig,vuln --skip-db-update --skip-check-update \
		--file-patterns "pip:requirements-ci.txt" --list-all-pkgs \
		--format json --output $(OUT_DIR)/trivy-report.json --skip-dirs .git .
	trivy convert --format sarif --output $(OUT_DIR)/public/security/trivy-results.sarif \
		$(OUT_DIR)/trivy-report.json
	cd /opt/trivy-templates && trivy convert --format template --template "@contrib/html.tpl" \
		--output $(OUT_DIR)/public/security/index.html $(OUT_DIR)/trivy-report.json
	trivy convert --format cyclonedx \
		--output $(OUT_DIR)/public/sbom/sbom.cdx.json $(OUT_DIR)/trivy-report.json
	$(PYTHON) scripts/ci/sbom_html.py --sbom $(OUT_DIR)/public/sbom/sbom.cdx.json \
		--output $(OUT_DIR)/public/sbom/index.html

ci-allure: ## Run tests with Allure results and generate historical trends
	$(PYTHON) scripts/ci/allure.py --root . --output $(OUT_DIR)/public/allure \
		--history $(OUT_DIR)/allure-history --results $(OUT_DIR)/allure-results

ci-pages-index: ## Generate the static DevSecOps report landing page
	$(PYTHON) scripts/ci/pages.py landing --public $(OUT_DIR)/public

ci-pages-history: ## Restore Allure history from the previous gh-pages bundle
	$(HOST_PYTHON) scripts/ci/pages.py history --source "$(SOURCE)" --destination "$(OUT_DIR)/allure-history"

ci-report-dir: ## Export the Pages destination for the current ref
	$(HOST_PYTHON) scripts/ci/pages.py destination --git-ref "$(GIT_REF)" --ref-name "$(REF_NAME)" \
		$(if $(GITHUB_OUTPUT),--github-output "$(GITHUB_OUTPUT)",)

ci-pages-configure: ## Ensure GitHub Pages publishes the gh-pages branch
	$(HOST_PYTHON) scripts/ci/configure_pages.py --repository "$(REPOSITORY)"


ci-report: ## Merge job fragments into Markdown, HTML and JSON
	$(PYTHON) scripts/ci/report.py --workflow "$(WORKFLOW)" --parts $(OUT_DIR)/parts \
		--output $(OUT_DIR) --needs-file $(OUT_DIR)/needs.json

act-build: ## Execute the Build workflow through Act and disposable Build Containers
	MODE=$(MODE) bash scripts/act/act.sh build.yml

act-iac: ## Execute advisory IaC rendering and policy checks locally
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-iac

act-publish: ## Dry-run publishing with the persistent local registry only
	@bash scripts/act/registry.sh up
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-publish \
		"REGISTRY=127.0.0.1:$(NIGU_REGISTRY_PORT)" "LOCAL=1"

registry-up: ## Start the persistent local OCI registry
	bash scripts/act/registry.sh up

registry-status: ## Check the persistent local OCI registry
	bash scripts/act/registry.sh status

registry-down: ## Stop the local registry without deleting its volume
	bash scripts/act/registry.sh down

container-catalog: ## Run catalog in an ephemeral Build Container
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-catalog

container-plan: ## Run plan in an ephemeral Build Container
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-plan "MODULES=$(MODULES)"

container-quality: ## Run quality checks in an ephemeral Build Container
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-quality

container-module: ## Run one module in an ephemeral Build Container
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-module "ID=$(ID)" "TYPE=$(TYPE)"

container-iac: ## Run advisory IaC checks in an ephemeral Build Container
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-iac

container-publish: ## Run local registry publication in an ephemeral Build Container
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-publish \
		"REGISTRY=$(REGISTRY)" "LOCAL=$(LOCAL)"

container-report: ## Generate merged reports in an ephemeral Build Container
	NEEDS="$$NEEDS_JSON" MODE=$(MODE) bash scripts/act/run-build-container.sh ci-report "WORKFLOW=$(WORKFLOW)"

container-report-output: ## Export a generated plan as workflow outputs
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-plan-output "GITHUB_OUTPUT=/output/github-output"
	@cp report/act/github-output "$(GITHUB_OUTPUT)"

container-retention: ## Generate retention reports in an ephemeral Build Container
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-retention "APPLY=$(APPLY)"

container-security-reports: ## Generate security and SBOM reports in a Build Container
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-security-reports

container-allure: ## Generate Allure reports in a Build Container
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-allure

container-pages-index: ## Generate the static report landing page
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-pages-index

container-release: ## Create a tag release inside a trusted Build Container
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-release

deploy: ## Validate a named future deployment target; runtime deployment is not implemented in S1
	@test -n "$(VPS)" || (echo "VPS= is required" >&2; exit 2)
	$(MAKE) manifest-validate MODE=$(MODE)
	@echo "S1 validates '$(VPS)'; deployment begins in a later stage" >&2

tenant-package: ## Build one tenant package in an ephemeral Build Container
	@test -n "$(PRODUCT)" && test -n "$(ID)" || (echo "PRODUCT= and ID= are required" >&2; exit 2)
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-module \
		"ID=tenant-$(PRODUCT)-$(ID)"

image-build: ## Build and scan one image module in an ephemeral Build Container
	@test -n "$(ID)" || (echo "ID= is required" >&2; exit 2)
	MODE=$(MODE) bash scripts/act/run-build-container.sh ci-module "ID=$(ID)"
