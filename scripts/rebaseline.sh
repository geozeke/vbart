#!/usr/bin/env bash
set -euo pipefail

info()  { echo -e "\033[1;34m[INFO]\033[0m  $*"; }
error() { echo -e "\033[1;31m[ERROR]\033[0m $*" >&2; }

# Get the directory where the script resides
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYPROJECT="$PROJECT_ROOT/pyproject.toml"

# --- Must be inside a repo ---
if ! git -C "$PROJECT_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  error "Must be run inside a Git repository."
  exit 1
fi

# --- Detect default branch ---
default_branch=$(
  git -C "$PROJECT_ROOT" remote show origin 2>/dev/null | \
  grep 'HEAD branch' | awk '{print $NF}'
)
if [[ -z "$default_branch" ]]; then
  default_branch="main"
  info "Default branch not found; assuming 'main'."
fi

# --- Current branch ---
current_branch=$(git -C "$PROJECT_ROOT" symbolic-ref --short HEAD)

# --- Prevent rebasing default branch ---
if [[ "$current_branch" == "$default_branch" ]]; then
  error "You are on '$default_branch'. Cannot rebase this branch."
  exit 1
fi

# --- Must be clean ---
CMD1="git -C $PROJECT_ROOT diff --quiet"
CMD2="git -C $PROJECT_ROOT diff --cached --quiet"
if ! $CMD1 || ! $CMD2; then
  error "Working tree is dirty. Commit or stash first."
  exit 1
fi

# --- Confirm branch is related to default branch ---
base_commit=$(git -C "$PROJECT_ROOT" merge-base HEAD origin/${default_branch})
if [[ -z "$base_commit" ]]; then
  error "No common ancestor with '${default_branch}'. Aborting."
  exit 1
fi

info "Parent is '${default_branch}'. Proceeding with rebase."
info "Fetching latest from origin..."
git fetch origin

info "Rebasing '${current_branch}' onto origin/${default_branch}..."
if ! git -C "$PROJECT_ROOT" rebase "origin/${default_branch}"; then
  error "Rebase failed. Fix conflicts and run 'git rebase --continue'."
  exit 1
fi

info "Force pushing rebased branch..."
git -C "$PROJECT_ROOT" push --force-with-lease

info "✅ Rebase complete!"
