set shell := ["bash", "-eu", "-o", "pipefail", "-c"]
project_name := "vbart"

# --------------------------------------------
# Private handler for commits
_commit latest:
    #!/usr/bin/env bash
    git add --update CHANGELOG.md pyproject.toml uv.lock
    if git diff --cached --quiet; then
        echo "No release changes found in CHANGELOG.md, pyproject.toml, or uv.lock."
        exit 1
    fi
    git commit -m "Bump version"
    if [[ "{{latest}}" == "true" ]]; then
        bash ./scripts/release_tags.sh --latest
    else
        bash ./scripts/release_tags.sh
    fi
    git push origin main

# --------------------------------------------
# Open a generated HTML report in the default browser
_display_webpage web_path:
    #!/usr/bin/env python3
    import webbrowser
    from pathlib import Path
    p = Path(".").resolve()/"{{web_path}}"
    if not p.exists():
        raise SystemExit(f"File not found: {p}")
    url = f"file://{p}"
    print(f"Coverage report: {url}")
    webbrowser.open(url, new=2)

# --------------------------------------------
# Load PyPI publishing secrets
_load_publish_secrets:
    #!/usr/bin/env bash
    if [ ! -f "$HOME/.secrets" ]; then
        echo 'Missing "$HOME/.secrets"'
        exit 1
    fi
    set -a
    . "$HOME/.secrets"
    set +a

# --------------------------------------------

# Require initial setup to be complete
_require_setup:
    #!/usr/bin/env bash
    if [ ! -f .init/setup ]; then
        echo 'Please run "just setup" first'
        exit 1
    fi

# --------------------------------------------

# Build package for publishing
build:
    rm -rf dist
    uv build

# --------------------------------------------

# Bump the project version and generate changelog
bump version:
    #!/usr/bin/env bash
    new_version="{{version}}"
    new_version="${new_version#v}"
    git cliff --unreleased --tag "$new_version" --prepend CHANGELOG.md
    tmp_changelog="$(mktemp)"
    awk '
        NR == 1 { print; prev = $0; next }
        /^## / && prev !~ /^[[:space:]]*$/ { print "" }
        { print; prev = $0 }
    ' CHANGELOG.md > "$tmp_changelog"
    mv "$tmp_changelog" CHANGELOG.md
    tmp_file="$(mktemp)"
    awk -v version="$new_version" '
        BEGIN { replaced = 0 }
        /^version = "/ && !replaced {
            print "version = \"" version "\""
            replaced = 1
            next
        }
        { print }
    ' pyproject.toml > "$tmp_file"
    mv "$tmp_file" pyproject.toml
    just sync

# --------------------------------------------

# Clean python runtime and build artifacts
clean:
    echo "Cleaning python runtime and build artifacts"
    rm -rf build dist .*cache htmlcov
    find . -type d -name __pycache__ -exec rm -rf {} \; -prune
    find . -type d -name .ipynb_checkpoints -exec rm -rf {} \; -prune
    find . -type d -name .pytest_cache -exec rm -rf {} \; -prune
    find . -type d -name .eggs -exec rm -rf {} \; -prune
    find . -type d -name '*.egg-info' -exec rm -rf {} \; -prune
    find . -type f -name '*.egg' -delete
    find . -type f -name '*.pyc' -delete
    find . -type f -name '*.pyo' -delete
    find . -type f -name '*.coverage' -delete

# --------------------------------------------

# Commit, push, update semantic version, EXCLUDE the "latest" tag
commit:
    just _commit false

# --------------------------------------------

# Commit, push, update semantic version, INCLUDE the "latest" tag
commit-latest:
    just _commit true

# --------------------------------------------

# Run tests with coverage reporting
coverage:
    uv run pytest --tb=short --cov --cov-report=term-missing --cov-report=html

# --------------------------------------------

# Run coverage and open HTML report in browser
coverage-open: coverage
    just _display_webpage "htmlcov/index.html"

# --------------------------------------------

# Show help
default: help

# --------------------------------------------

# Provision development dependencies
dev: _require_setup
    #!/usr/bin/env bash
    export UV_PYTHON_PREFERENCE=only-managed
    uv sync --all-groups --frozen
    touch .init/dev

# --------------------------------------------

# Show available recipes
help:
    @just --list

# --------------------------------------------

# Run lint checks
lint:
    uv run ruff check .

# --------------------------------------------

# Publish package to pypi.org for production
publish-production: _load_publish_secrets build
    #!/usr/bin/env bash
    : "${PYPI_PROD:?Missing PYPI_PROD in $HOME/.secrets}"
    uv publish --publish-url https://upload.pypi.org/legacy/ -t "$PYPI_PROD"

# --------------------------------------------

# Publish package to test.pypi.org for testing
publish-test: _load_publish_secrets build
    #!/usr/bin/env bash
    : "${PYPI_TEST:?Missing PYPI_TEST in $HOME/.secrets}"
    uv publish --publish-url https://test.pypi.org/legacy/ -t "$PYPI_TEST"

# --------------------------------------------

# Rebase to the main branch
rebase:
    bash ./scripts/rebaseline.sh

# --------------------------------------------

# Reset the project state
reset: clean
    echo "Resetting project state"
    rm -rf .init .mypy_cache .ruff_cache .venv

# --------------------------------------------

# Initialize the project environment
setup:
    #!/usr/bin/env bash
    if [ ! -f .init/setup ]; then
        if ! command -v uv >/dev/null 2>&1; then
            echo "{{project_name}} requires uv. See README for instructions."
            exit 1
        fi
        mkdir -p scratch .init
        touch .init/setup
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

# Sync dependencies with the lockfile (frozen)
sync: _require_setup
    #!/usr/bin/env bash
    if [ -f .init/dev ]; then
        uv sync --all-groups --frozen
    else
        uv sync --no-dev --frozen
    fi

# --------------------------------------------

# Generate release tags
tags:
    bash ./scripts/release_tags.sh

# --------------------------------------------

# Run pytest with --tb=short option
test:
    uv run pytest --tb=short

# --------------------------------------------

# Run static type checks
typecheck:
    uv run mypy src

# --------------------------------------------

# Upgrade dependencies
upgrade: _require_setup
    #!/usr/bin/env bash
    if [ -f .init/dev ]; then
        uv sync --upgrade --all-groups
    else
        uv sync --upgrade --no-dev
    fi
