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
