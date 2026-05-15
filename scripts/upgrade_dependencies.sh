#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

export UV_CACHE_DIR="${UV_CACHE_DIR:-.uv-cache}"

if [ -n "$(git status --porcelain)" ]; then
    echo "Cannot upgrade dependencies with a dirty worktree."
    echo "Commit, stash, or discard local changes before running just upgrade."
    exit 1
fi

before_versions="$(mktemp)"
commit_message="$(mktemp)"
cleanup() {
    rm -f "$before_versions" "$commit_message"
}
trap cleanup EXIT

uv run --with tomli python scripts/dependency_upgrade_commit.py snapshot \
    --lockfile uv.lock \
    --output "$before_versions"

if [ -f .init/dev ]; then
    uv sync --upgrade --all-groups
else
    uv sync --upgrade --no-dev
fi

if ! uv run --with tomli python scripts/dependency_upgrade_commit.py message \
    --pyproject pyproject.toml \
    --lockfile uv.lock \
    --before "$before_versions" \
    --output "$commit_message"; then
    git restore -- pyproject.toml uv.lock
    echo "No first-order dependency updates found; no commit created."
    exit 0
fi

git add pyproject.toml uv.lock

if git diff --cached --quiet; then
    echo "No dependency file changes found; no commit created."
    exit 0
fi

git commit -F "$commit_message"
echo "Created local dependency upgrade commit. Review it before pushing."
