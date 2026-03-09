set shell := ["bash", "-eu", "-o", "pipefail", "-c"]
project_name := "vbart"

# Show help
default: help

# --------------------------------------------

# Initialize the project environment
setup:
    #!/usr/bin/env bash
    if [ ! -f .init/setup ]; then
        if ! command -v uv >/dev/null 2>&1; then
            echo "{{project_name}} requires uv. See README for instructions."
            exit 1
        fi
        mkdir -p scratch .init run
        touch .init/setup
        cp ./scripts/* ./run
        find ./run -name '*.sh' -exec chmod 744 {} \;
        export UV_PYTHON_PREFERENCE=only-managed
        uv sync --frozen --no-dev
    else
        echo "Initial setup is already complete. If you are having issues, run:"
        echo
        echo "just reset"
        echo "just setup"
        echo
    fi

# --------------------------------------------

# Provision development dependencies
dev:
    #!/usr/bin/env bash
    if [ ! -f .init/setup ]; then
        echo 'Please run "just setup" first'
        exit 1
    fi
    export UV_PYTHON_PREFERENCE=only-managed
    uv sync --all-groups --frozen
    touch .init/dev

# --------------------------------------------

# Upgrade dependencies
upgrade:
    #!/usr/bin/env bash
    if [ ! -f .init/setup ]; then
        echo 'Please run "just setup" first'
        exit 1
    fi

    cp -f ./scripts/* ./run
    find ./run -name '*.sh' -exec chmod 744 {} \;

    if [ -f .init/dev ]; then
        uv sync --upgrade --all-groups
    else
        uv sync --upgrade --no-dev
    fi

# --------------------------------------------

# Sync dependencies with the lockfile (frozen)
sync:
    #!/usr/bin/env bash
    if [ ! -f .init/setup ]; then
        echo 'Please run "just setup" first'
        exit 1
    fi

    if [ -f .init/dev ]; then
        uv sync --all-groups
    else
        uv sync --no-dev
    fi

# --------------------------------------------

# Clean python runtime and build artifacts
clean:
    echo "Cleaning python runtime and build artifacts"
    rm -rf build/
    rm -rf dist/
    find . -type d -name __pycache__ -exec rm -rf {} \; -prune
    find . -type d -name .ipynb_checkpoints -exec rm -rf {} \; -prune
    find . -type d -name .pytest_cache -exec rm -rf {} \; -prune
    find . -type d -name .eggs -exec rm -rf {} \; -prune
    find . -type d -name htmlcov -exec rm -rf {} \; -prune
    find . -type d -name *.egg-info -exec rm -rf {} \; -prune
    find . -type f -name *.egg -delete
    find . -type f -name *.pyc -delete
    find . -type f -name *.pyo -delete
    find . -type f -name *.coverage -delete

# --------------------------------------------

# Reset the project state
reset: clean
    echo "Resetting project state"
    rm -rf .init .mypy_cache .ruff_cache .venv run htmlcov

# --------------------------------------------

# Build package for publishing
build: 
	rm -rf dist
	uv build

# --------------------------------------------

# Publish package to pypi.org for production
publish-production: build
    #!/usr/bin/env bash
    set -a
    eval $(grep '^PYPI_' "$HOME/.secrets")
    uv publish --publish-url https://upload.pypi.org/legacy/ -t "$PYPI_PROD"

# --------------------------------------------

# Publish package to test.pypi.org for testing
publish-test: build
    #!/usr/bin/env bash
    set -a
    eval $(grep '^PYPI_' "$HOME/.secrets")
    uv publish --publish-url https://test.pypi.org/legacy/ -t "$PYPI_TEST"

# --------------------------------------------

# Bump the project version and generate changelog
bump version:
    uv run run/bump.py {{version}}
    just sync

# --------------------------------------------

# Commit, push changes, update tags
commit:
    git add .
    git commit -m "Bump version"
    git push origin main
    just tags

# --------------------------------------------

# Generate release tags
tags:
    ./run/release_tags.sh

# --------------------------------------------

# Rebase to the main branch
rebase:
    ./run/rebaseline.sh

# --------------------------------------------

# Show available recipes
help:
    @just --list
