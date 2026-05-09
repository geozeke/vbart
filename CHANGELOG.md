## 0.3.1 (2026-05-08)

### 🐛 Bug Fixes

- Remove dupes in cliff.toml (76660c5)

### 🛠️ 📦 Development Dependencies

- Bump ruff from 0.15.11 to 0.15.12 (fd49b79)
- Bump mypy from 1.20.2 to 2.0.0 (c6005eb)

### ⚙️ Miscellaneous Tasks

- Add documentation consistency check (2d35910)
- Set default codex model to 5.5 medium (1f2edba)

### 🚜 Refactor

- Streamline tagging and release (c0cffa9)

## 0.3.0 (2026-04-24)

### 🐛 Bug Fixes

- Remove circular dependency (9461c77)
- Harden checking for docker runtime (29080e6)
- Make "help" the default in the justfile (0d75ea4)
- Fix shell environment leak (0066544)

### 🛠️ Changes

- Drop python 3.9 and add 3.14 (a8cb6b5)

### 🗑️ Removed

- Remove /run directory (b2ffce6)

### 🧪 Testing

- Add unit tests (f52ab22)
- Fix errors in Windows test scripts (a367017)

### 🛠️ 📦 Development Dependencies

- Update LICENSE metadata (d9b2493)
- Bump ruff from 0.15.8 to 0.15.9 (721642e)
- Bump mypy from 1.19.1 to 1.20.0 (86db7a3)
- Bump ruff from 0.15.9 to 0.15.10 (c4617e8)
- Bump ruff from 0.15.10 to 0.15.11 (7050620)
- Bump mypy from 1.20.0 to 1.20.1 (d55ab9d)
- Bump mypy from 1.20.1 to 1.20.2 (f742179)

### 📚 Documentation

- Lint README (ae81299)
- Lint argparse messages (381303c)
- Lint Markdown Files (995ed0f)
- Lint docstrings (5ffa773)
- Lint CHANGELOG (d2ce127)

### 🚀 Features

- Allow for selective tagging (13906e9)
- Add Windows support (657c502)

### ⚙️ Miscellaneous Tasks

- Lint justfile (124ee85)
- Lint justfile (15c1c63)
- Initialize codex tooling (6a1341d)
- Use updated cliff.toml and justfile (86de5a7)
- Implement code coverage (dd21c38)
- Cleanup .gitignore (87f3a71)
- Conform licensing to the standard (1f01d8d)
- Lint AGENTS.md (091c9b1)
- Add CI pipeline for linting and testing (e6bca3e)
- Cleanup justfile (51a9bad)
- Lint justfile (26e6495)
- Host logo within repo (f0a48ba)
- Conduct metadata audit (5bb3673)
- Add truthiness preference to AGENTS.md (d9b2979)
- Unfreeze syncing in justfile (e491cf6)

### 🚜 Refactor

- Improve handling of Dockerfile (cf260bb)

## 0.2.1 (2026-03-27)

### 🛠️ Changes

- Migrate release generation to cliff (d92e459)

### 📦 Runtime Dependencies

- Bump requests from 2.32.5 to 2.33.0 in the uv group across 1
  directory (c2bbcdd)

### 🛠️ 📦 Development Dependencies

- Bump ruff from 0.15.5 to 0.15.6 (50cb8dd)
- Bump ruff from 0.15.6 to 0.15.7 (79b2d9f)
- Bump ruff from 0.15.7 to 0.15.8 (f749dc7)
- Bump upper bound for uv-build to 0.12 (54d9315)

### 📚 Documentation

- Lint CHANGELOG for markdown errors (338ee1f)
- Lint config.toml (11dd55a)
- Standardize changelog header format (d3ba640)
- Update logo (70e5e34)

## 0.2.0 (2026-03-06)

## ⛓️‍💥 BREAKING

- This version drops support for python 3.9

### 🚀 New Features

- Add docs label to release.yml by @geozeke in
  <https://github.com/geozeke/vbart/pull/18>

### 🐛 Bug Fixes

- Pin upper bound for uv-build by @geozeke in
  <https://github.com/geozeke/vbart/pull/27>

### 📦 Dependency Updates

- Bump ruff from 0.14.11 to 0.14.13 by @dependabot[bot] in
  <https://github.com/geozeke/vbart/pull/19>
- Bump ruff from 0.14.13 to 0.14.14 by @dependabot[bot] in
  <https://github.com/geozeke/vbart/pull/21>
- Bump urllib3 from 2.5.0 to 2.6.3 in the uv group across 1
  directory by @dependabot[bot] in
  <https://github.com/geozeke/vbart/pull/20>
- Bump ruff from 0.14.14 to 0.15.0 by @dependabot[bot] in
  <https://github.com/geozeke/vbart/pull/22>
- Bump ruff from 0.15.0 to 0.15.1 by @dependabot[bot] in
  <https://github.com/geozeke/vbart/pull/23>
- Bump ruff from 0.15.1 to 0.15.2 by @dependabot[bot] in
  <https://github.com/geozeke/vbart/pull/24>
- Bump ruff from 0.15.2 to 0.15.4 by @dependabot[bot] in
  <https://github.com/geozeke/vbart/pull/25>
- Bump ruff from 0.15.4 to 0.15.5 by @dependabot[bot] in
  <https://github.com/geozeke/vbart/pull/28>

## 0.1.10 (2026-01-11)

### 🚀 New Features

- Add release.yml for formatted release messages by @geozeke in
  <https://github.com/geozeke/vbart/pull/17>

## [0.1.9][0.1.9] - 2026-01-09

### Development Dependency Updates

- Bump ruff from 0.14.10 to 0.14.11 ([#16][pull16])
- Bump ruff from 0.14.9 to 0.14.10 ([#14][pull14])
- Bump mypy from 1.19.0 to 1.19.1 ([#15][pull15])
- Bump ruff from 0.14.8 to 0.14.9 ([#13][pull13])
- Bump ruff from 0.14.6 to 0.14.8 ([#11][pull11])
- Bump mypy from 1.18.2 to 1.19.0 ([#12][pull12])
- Bump ruff from 0.14.5 to 0.14.6 ([#10][pull10])
- Bump ruff from 0.14.4 to 0.14.5 ([#9][pull9])
- Bump ruff from 0.14.3 to 0.14.4 ([#8][pull8])
- Bump ruff from 0.14.2 to 0.14.3 ([#7][pull7])

### Changed

- Update copyright years on LICENSE.

### Added

- Force uv sync to prefer managed python versions.

## [0.1.8][0.1.8] - 2025-10-07

### Changed

- Refactor version numbering.
- Upgrade build backend from hatchling to uv_build.
- Use standard emoji for PASS/FAIL.
- [requests][requests] bumped `2.32.4`.

## [0.1.7][0.1.7] - 2025-05-23

### Changed

- Maintenance release to synchronize repository tags.

## [0.1.6][0.1.6] - 2025-03-06

### Removed

- Drop support for Python 3.8 ([#5][issue5])

## [0.1.5][0.1.5] - 2024-11-15

_Initial Public Release._

[0.1.5]: https://github.com/geozeke/parser201/releases/tag/v0.1.5
[0.1.6]: https://github.com/geozeke/parser201/releases/tag/v0.1.6
[0.1.7]: https://github.com/geozeke/parser201/releases/tag/v0.1.7
[0.1.8]: https://github.com/geozeke/parser201/releases/tag/v0.1.8
[0.1.9]: https://github.com/geozeke/parser201/releases/tag/v0.1.9
[issue5]: https://github.com/geozeke/vbart/issues/5
[pull10]: https://github.com/geozeke/vbart/pull/10
[pull11]: https://github.com/geozeke/vbart/pull/11
[pull12]: https://github.com/geozeke/vbart/pull/12
[pull13]: https://github.com/geozeke/vbart/pull/13
[pull14]: https://github.com/geozeke/vbart/pull/14
[pull15]: https://github.com/geozeke/vbart/pull/15
[pull16]: https://github.com/geozeke/vbart/pull/16
[pull7]: https://github.com/geozeke/vbart/pull/7
[pull8]: https://github.com/geozeke/vbart/pull/8
[pull9]: https://github.com/geozeke/vbart/pull/9
[requests]: https://github.com/psf/requests
