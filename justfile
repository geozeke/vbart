set shell := ["bash", "-eu", "-o", "pipefail", "-c"]
project_name := "vbart"

# Show available recipes
default:
    @just --list

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

# Bump the project version and generate changelog
bump version:
    uv run python -m scripts.bump_version {{version}}

# Preview release-note-visible commits
changelog:
    git-cliff --unreleased

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

# Format Python files and apply fixable lint rules
format:
    uv run ruff check --fix .
    uv run ruff format .

# Run lint and formatting checks
lint:
    uv run ruff check .
    uv run ruff format --check .

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
        uv sync --frozen --all-groups
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
    uv sync --all-groups

# --------------------------------------------

# Run the complete local quality-check suite
check: lint typecheck test

# Generate and push the release tag
tag-release:
    uv run python -m scripts.tag_release

# --------------------------------------------

# Run pytest with --tb=short option
test:
    uv run pytest --tb=short

# --------------------------------------------

# Run static type checks
typecheck:
    uv run mypy src scripts
