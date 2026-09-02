# AGENTS

This repository contains `vbart`, a Python CLI for backing up and
restoring Docker named volumes.

## Scope

- Runtime package code lives under `src/vbart/`.
- Runnable module entry point is `src/vbart/__main__.py`.
- CLI parser and dispatch code lives in `src/vbart/app.py`.
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
- Prefer truthiness checks like `if value:` and `if not value:` over
  explicit empty or `None` comparisons when they are semantically
  equivalent.
- Use strict NumPy-style docstrings for all function, class, and
  module docstrings.
- When asked to review or modify `.gitignore`, also check
  whether Git global excludes are configured (for example,
  `git config --global core.excludesfile`) and factor that
  into recommendations.
- Wrap Markdown prose to 72 characters when practical, but do not
  break links, code spans, tables, or other formatting that would be
  harmed by wrapping.

## Documentation

- When making changes, ensure documentation and metadata remain
  consistent. This includes documents in instructions/ and todo/ (if
  they exist), and files like README.md and AGENTS.md. Also include
  argparse messages, docstrings, and code comments.

## Release Workflow

- Update code and documentation before preparing a release.
- Use Conventional Commit pull-request titles. Preview user-facing release
  notes with `just changelog`.
- Create a release branch, such as `release/v0.5.0` or
  `release/v0.5.0rc1`.
- Run `just bump <version>` to update `CHANGELOG.md`, archived
  changelog files under `changelogs/`, `pyproject.toml`, and `uv.lock`.
  Stable releases use versions such as `0.5.0`; prereleases use canonical
  PEP 440 forms such as `0.5.0b1` and `0.5.0rc1`.
- Commit the release changes, open a pull request, and merge it after
  `just check` and CI pass.
- Update local `main` with `git pull --ff-only origin main`.
- Run `just tag-release` to create and push one annotated version tag.
- Pushing a `v...` version tag validates metadata, runs `just check`,
  builds and smoke-tests distributions, and publishes prereleases to
  TestPyPI or stable releases to PyPI through Trusted Publishing.
- The `latest` tag is mutable and must not be treated as an immutable
  release record. CI moves it only after stable PyPI and GitHub release
  publication succeed; it is never moved for prereleases.
- Configure GitHub `testpypi` and `pypi` environments with matching
  Trusted Publishers before the first release.

## Dependency Maintenance

- Dependabot opens grouped weekly direct-dependency updates for uv and
  GitHub Actions. Eligible minor and patch updates are squash-auto-merged
  after their guarded metadata workflow succeeds.

## Verification

- Read project metadata in `pyproject.toml` before changing packaging
  behavior.
- Use `uv`/`just` workflows already defined in `justfile` when relevant.
- Use `just check` for the complete local quality suite.
- Prefer lightweight checks first:
  - `python -m vbart -h` or installed `vbart -h`
  - `ruff format`
  - `ruff`
  - `mypy`

## Notes

- The project depends on a working Docker runtime that is reachable
  through the Docker Python SDK.
- Backup and restore behavior is container-based and uses the helper
  image built from a generated Dockerfile.
