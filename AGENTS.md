# AGENTS

This repository contains `vbart`, a Python CLI for backing up and
restoring Docker named volumes.

## Scope

- Runtime package code lives under `src/vbart/`.
- CLI entry point is `src/vbart/app.py`.
- Command implementations live in:
  - `src/vbart/backup.py`
  - `src/vbart/backups.py`
  - `src/vbart/restore.py`
  - `src/vbart/refresh.py`
- Argument parser modules live under `src/vbart/parsers/`.
- Release and maintenance scripts live under `scripts/`.

## Working Rules

- Do not traverse or modify `.venv/`.
- Prefer small, targeted changes that preserve the existing CLI
  behavior.
- Keep the package dependency footprint minimal.
- Preserve the current source layout unless a refactor is explicitly
  requested.
- Do not traverse cache or generated-state directories such as
  `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `__pycache__/`,
  or `.cache/` unless the task explicitly requires it.
- Prefer reading `README.md`, `pyproject.toml`, and files under
  `src/vbart/` first.
- Use `rg` for searches and `just` or `uv` for common project tasks when
  needed.
- Prefer `pathlib.Path` objects over raw path strings where
  practical.
- Use strict NumPy-style docstrings for all function, class, and
  module docstrings.
- When asked to review or modify `.gitignore`, also check
  whether Git global excludes are configured (for example,
  `git config --global core.excludesfile`) and factor that
  into recommendations.
- Wrap Markdown prose to 72 characters when practical, but do not
  break links, code spans, tables, or other formatting that would be
  harmed by wrapping.

## Verification

- Read project metadata in `pyproject.toml` before changing packaging
  behavior.
- Use `uv`/`just` workflows already defined in `justfile` when relevant.
- Prefer lightweight checks first:
  - `python -m vbart -h` or installed `vbart -h`
  - `ruff`
  - `mypy`

## Notes

- The project depends on a working Docker runtime that is reachable
  through the Docker Python SDK.
- Backup and restore behavior is container-based and uses the helper
  image built from a generated Dockerfile.
