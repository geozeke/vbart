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
	uv sync --no-dev --frozen
	@echo "✅ Setup complete!"
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
	@if [ ! -f ".init/setup" ]; then \
		echo "❌ Error: Setup is required. Run 'make setup' first."; \
		exit 1; \
	fi
	uv sync --frozen
	@touch .init/dev
	@echo "✅ Development dependencies installed!"

# --------------------------------------------

.PHONY: upgrade
upgrade: ## upgrade project dependencies
	@if [ ! -f ".init/setup" ]; then \
		echo "❌ Error: Setup is required before upgrading. Run 'make setup' first."; \
		exit 1; \
	fi
	@if [ -f ".init/dev" ]; then \
		uv sync --upgrade; \
	else \
		uv sync --no-dev --upgrade; \
	fi

# --------------------------------------------

.PHONY: reset
reset: clean ## remove venv, artifacts, and init directory
	@echo Resetting project state
	rm -rf .init .ruff_cache .mypy_cache .venv

# --------------------------------------------

.PHONY: build
build: ## build package for publishing
	rm -rf dist
	uv build

# --------------------------------------------

.PHONY: publish-production
publish-production: build ## publish package to pypi.org for production
	@if [ -z "${PYPITOKEN}" ]; then \
		echo "❌ Error: PYPITOKEN is not set!"; \
		exit 1; \
	fi
	uv publish --publish-url https://upload.pypi.org/legacy/ --token ${PYPITOKEN}

# --------------------------------------------

.PHONY: publish-test
publish-test: build ## publish package to test.pypi.org for testing
	@if [ -z "${TESTPYPITOKEN}" ]; then \
		echo "❌ Error: TESTPYPITOKEN is not set!"; \
		exit 1; \
	fi
	uv publish  --publish-url https://test.pypi.org/legacy/ \
		--token ${TESTPYPITOKEN}

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
	@echo "🚀 Available Commands 🚀"
	@echo "========================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk \
	'BEGIN {FS = ":.*?## "}; \
	{printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
