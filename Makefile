# ───── Config ─────────────────────────────────────────────────────────
SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

ROOT        := $(shell pwd)
CLI_DIR     := packages/devex-cli
FRAMEWORK_DIR := packages/platform-framework
CONVENTIONS := conventions/conventions.json
CLI_CONVENTIONS_COPY := $(CLI_DIR)/src/devex/_data/conventions.json

# ───── Meta ───────────────────────────────────────────────────────────
.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ───── Prerequisites ──────────────────────────────────────────────────
.PHONY: doctor
doctor: ## Check host prerequisites
	@missing=0; \
	for cmd in uv node pnpm; do \
	  if ! command -v $$cmd >/dev/null 2>&1; then echo "✗ missing: $$cmd"; missing=1; else echo "✓ $$cmd"; fi; \
	done; \
	[ $$missing -eq 0 ] || { echo "Install missing tools and retry."; exit 1; }

# ───── Single source of truth ─────────────────────────────────────────
.PHONY: sync-conventions
sync-conventions: ## Copy canonical conventions.json into the CLI package data
	cp $(CONVENTIONS) $(CLI_CONVENTIONS_COPY)
	@echo "✓ synced $(CONVENTIONS) → $(CLI_CONVENTIONS_COPY)"

.PHONY: check-conventions
check-conventions: ## Fail if the CLI's bundled conventions copy has drifted (CI gate)
	@diff -q $(CONVENTIONS) $(CLI_CONVENTIONS_COPY) >/dev/null \
	  && echo "✓ conventions in sync" \
	  || { echo "✗ conventions drift — run 'make sync-conventions'"; exit 1; }

# ───── Install ────────────────────────────────────────────────────────
.PHONY: install
install: install-cli install-framework ## Install both packages' dev deps

.PHONY: install-cli
install-cli: ## Install the Python CLI (uv)
	cd $(CLI_DIR) && uv sync --extra dev

.PHONY: install-framework
install-framework: ## Install the TypeScript framework (pnpm)
	cd $(FRAMEWORK_DIR) && pnpm install

# ───── Test ───────────────────────────────────────────────────────────
.PHONY: test
test: test-cli test-framework ## Run all tests

.PHONY: test-cli
test-cli: ## CLI tests (pytest + Hypothesis)
	cd $(CLI_DIR) && uv run pytest --tb=short -q

.PHONY: test-framework
test-framework: ## Framework tests (Vitest)
	cd $(FRAMEWORK_DIR) && pnpm test

# ───── Lint & typecheck ───────────────────────────────────────────────
.PHONY: lint
lint: lint-cli lint-framework ## Lint both packages

.PHONY: lint-cli
lint-cli: ## Ruff (Python)
	cd $(CLI_DIR) && uv run ruff check .

.PHONY: lint-framework
lint-framework: ## tsc --noEmit (TypeScript)
	cd $(FRAMEWORK_DIR) && pnpm lint

# ───── Build ──────────────────────────────────────────────────────────
.PHONY: build
build: ## Build the framework (dist/) — the CLI builds at install time
	cd $(FRAMEWORK_DIR) && pnpm build

# ───── Governance ─────────────────────────────────────────────────────
.PHONY: protect-main
protect-main: ## Apply the main-branch ruleset (PR + 2 reviewers); needs a public repo or GitHub Pro
	bash scripts/apply-branch-protection.sh

# ───── Local dev env (offline demo via LocalStack) ────────────────────
.PHONY: localstack-up
localstack-up: ## Start LocalStack (local AWS emulator) — see docs/runbooks/local-dev-env.md
	docker compose up -d localstack

.PHONY: localstack-down
localstack-down: ## Stop LocalStack and remove its volume
	docker compose down -v

# ───── Utilities ──────────────────────────────────────────────────────
.PHONY: clean
clean: ## Remove generated artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf $(FRAMEWORK_DIR)/dist $(CLI_DIR)/dist 2>/dev/null || true
