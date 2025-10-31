all: help

# --------------------------------------------

.PHONY: setup
setup: ## setup project with runtime dependencies
ifeq (,$(wildcard .init/setup))
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "❌ Error: 'uv' is not installed. See README for instructions"; \
		exit 1; \
	fi
	mkdir -p scratch files run .init
	touch .init/setup
	cp ./scripts/* ./run
	find ./run -name '*.sh' -exec chmod 744 {} \;
	uv sync --frozen --no-dev
	@echo "✅ Setup complete."
else
	@echo "Initial setup is already complete. If you are having issues, run:"
	@echo
	@echo "make reset"
	@echo "make setup"
	@echo
endif

# --------------------------------------------

.PHONY: dev
dev: ## add development dependencies (run make setup first)
ifeq (,$(wildcard .init/setup))
	@echo "Please run \"make setup\" first" ; exit 1
endif
	uv sync --all-groups --frozen
	@touch .init/dev

# --------------------------------------------

.PHONY: upgrade
upgrade: ## synchronize helper scripts and upgrade project dependencies
ifeq (,$(wildcard .init/setup))
	@echo "Please run \"make setup\" first" ; exit 1
endif
	cp -f ./scripts/* ./run
	find ./run -name '*.sh' -exec chmod 744 {} \;
ifeq (,$(wildcard .init/dev))
	uv sync --upgrade --no-dev
else
	uv sync --upgrade --all-groups
endif

# --------------------------------------------

.PHONY: sync
sync: ## sync dependencies with the lock file (use --frozen)
ifeq (,$(wildcard .init/setup))
	@echo "Please run \"make setup\" first" ; exit 1
endif

ifneq (,$(wildcard .init/dev))
	uv sync --all-groups
else
	uv sync --no-dev
endif

# --------------------------------------------

.PHONY: reset
reset: clean ## remove venv, artifacts, and init directory
	@echo Resetting project state
	rm -rf .init .ruff_cache .mypy_cache .venv run

# --------------------------------------------

.PHONY: tags
tags: ## Update project tags
	./run/release_tags.sh

# --------------------------------------------

.PHONY: build
build: ## build package for publishing
	rm -rf dist
	uv build

# --------------------------------------------

.PHONY: publish-production
publish-production: build ## publish package to pypi.org for production
	@set -a; eval "$$(grep '^PYPI_' $$HOME/.secrets)"; \
	uv publish --publish-url https://upload.pypi.org/legacy/ \
		--token "$$PYPI_PROD"

# --------------------------------------------

.PHONY: publish-test
publish-test: build ## publish package to test.pypi.org for testing
	@set -a; eval "$$(grep '^PYPI_' $$HOME/.secrets)"; \
	uv publish  --publish-url https://test.pypi.org/legacy/ \
		--token "$$PYPI_TEST"

# --------------------------------------------

.PHONY: clean
clean: ## cleanup python runtime and build artifacts
	@echo Cleaning python runtime and build artifacts
	@rm -rf build/
	@rm -rf dist/
	@find . -type d -name __pycache__ -exec rm -rf {} \; -prune
	@find . -type d -name .pytest_cache -exec rm -rf {} \; -prune
	@find . -type d -name .eggs -exec rm -rf {} \; -prune
	@find . -type d -name htmlcov -exec rm -rf {} \; -prune
	@find . -type d -name *.egg-info -exec rm -rf {} \; -prune
	@find . -type f -name *.egg -delete
	@find . -type f -name *.pyc -delete
	@find . -type f -name *.pyo -delete
	@find . -type f -name *.coverage -delete

# --------------------------------------------

.PHONY: help
help: ## show help
	@echo ""
	@echo "Available Commands"
	@echo "========================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk \
	'BEGIN {FS = ":.*?## "}; \
	{printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
