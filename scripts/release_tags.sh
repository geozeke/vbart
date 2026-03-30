#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 [-l|--latest]"
  echo "  -l, --latest tag and push 'latest'"
  exit 1
}

# Default
TAG_LATEST=false

# Parse flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    -l|--latest)
      TAG_LATEST=true
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

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

# Check if version tag already exists
if git -C "$PROJECT_ROOT" tag | grep -qx "$tag"; then
  echo "Error: Tag '$tag' already exists."
  exit 1
fi

# Create and push version tag
git -C "$PROJECT_ROOT" tag "$tag"
git -C "$PROJECT_ROOT" push origin "$tag"

# Optionally create and push "latest"
if [[ "$TAG_LATEST" == true ]]; then
  git -C "$PROJECT_ROOT" tag -f latest
  git -C "$PROJECT_ROOT" push origin -f latest
  echo "Tags '$tag' and 'latest' pushed successfully."
else
  echo "Tag '$tag' pushed successfully."
fi
