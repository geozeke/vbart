all: help

# --------------------------------------------

.PHONY: setup
setup: ## setup project with runtime dependencies
ifeq (,$(wildcard .init/setup))
	@(which poetry > /dev/null 2>&1) || \
	(echo "vbart requires poetry. See README for instructions."; exit 1)
	@if [ ! -d "./scratch" ]; then \
		mkdir -p scratch; \
	fi
	mkdir .init
	touch .init/setup
	poetry install --only=main
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
ifneq (,$(wildcard .init/setup))
	poetry install
	@touch .init/dev
else
	@echo "Please run \"make setup\" first"
endif

# --------------------------------------------

.PHONY: update
update: ## update vbart code and dependencies
	@echo Updating vbart
	git pull
	@echo Updating dependencies
ifeq (,$(wildcard .init/dev))
	poetry update --only=main
else
	poetry update
endif

# --------------------------------------------

.PHONY: reset
reset: clean ## remove venv, artifacts, and init directory
	@echo Resetting project state
	rm -rf .init .mypy_cache .venv

# --------------------------------------------

.PHONY: clean
clean: ## cleanup python runtime and build artifacts
	@echo Cleaning python runtime and build artifacts
	@find . -type d -name __pycache__ -exec rm -rf {} \; -prune
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
	@echo Please specify a target. Choices are:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk \
	'BEGIN {FS = ":.*?## "}; \
	{printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'