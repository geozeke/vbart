set shell := ["bash", "-eu", "-o", "pipefail", "-c"]
project_name := "vbart"

# Show help
default: help

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
    uv run python scripts/archive_changelog.py "$new_version"
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

# Run tests with coverage reporting
coverage:
    uv run pytest --tb=short --cov --cov-report=term-missing --cov-report=html

# --------------------------------------------

# Run coverage and open HTML report in browser
coverage-open: coverage
    just _display_webpage "htmlcov/index.html"

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
publish-production: build
    #!/usr/bin/env bash
    if [ ! -f "$HOME/.secrets" ]; then
        echo 'Missing "$HOME/.secrets"'
        exit 1
    fi
    set -a
    . "$HOME/.secrets"
    set +a
    : "${PYPI_PROD:?Missing PYPI_PROD in $HOME/.secrets}"
    uv publish --publish-url https://upload.pypi.org/legacy/ -t "$PYPI_PROD"

# --------------------------------------------

# Publish package to test.pypi.org for testing
publish-test: build
    #!/usr/bin/env bash
    if [ ! -f "$HOME/.secrets" ]; then
        echo 'Missing "$HOME/.secrets"'
        exit 1
    fi
    set -a
    . "$HOME/.secrets"
    set +a
    : "${PYPI_TEST:?Missing PYPI_TEST in $HOME/.secrets}"
    uv publish --publish-url https://test.pypi.org/legacy/ -t "$PYPI_TEST"

# --------------------------------------------

# Reset the project state
reset: clean
    echo "Resetting project state"
    rm -rf .init .venv

# --------------------------------------------

# Initialize the project environment
setup:
    #!/usr/bin/env bash
    if [ ! -f .init/setup ]; then
        if ! command -v uv >/dev/null 2>&1; then
            echo "{{project_name}} requires uv. See README for instructions."
            exit 1
        fi
        if ! command -v git >/dev/null 2>&1; then
            echo "{{project_name}} requires git. See README for instructions."
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
        uv sync --all-groups
    else
        uv sync --no-dev
    fi

# --------------------------------------------

# Generate release tag
tag-release:
    bash ./scripts/release_tags.sh

# --------------------------------------------

# Generate release tag and update latest
tag-release-latest:
    bash ./scripts/release_tags.sh --latest

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
    bash ./scripts/upgrade_dependencies.sh
