#!/usr/bin/env bash
set -euo pipefail

# Get the directory where the script resides
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYPROJECT="$PROJECT_ROOT/pyproject.toml"

# Extract version from pyproject.toml
version=$(grep -E '^version *= *"' "$PYPROJECT" | \
  sed -E 's/version *= *"([^"]+)"/\1/')
tag="v$version"

# Ensure we're on the main branch
current_branch=$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" != "main" ]]; then
  echo "Error: You are on branch '$current_branch'. Switch to 'main' to tag."
  exit 1
fi

# Ensure working directory is clean
if ! git -C "$PROJECT_ROOT" diff --quiet || \
   ! git -C "$PROJECT_ROOT" diff --cached --quiet; then
  echo "Error: Working directory is dirty. Commit or stash changes first."
  exit 1
fi

# Check if tag already exists
if git -C "$PROJECT_ROOT" tag | grep -qx "$tag"; then
  echo "Error: Tag '$tag' already exists."
  exit 1
fi

# Tag and push
git -C "$PROJECT_ROOT" tag "$tag"
git -C "$PROJECT_ROOT" tag -f latest
git -C "$PROJECT_ROOT" push origin "$tag"
git -C "$PROJECT_ROOT" push origin -f latest

echo "Tags '$tag' and 'latest' pushed successfully."
