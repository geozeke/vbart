# Changelog

All notable changes to vbart are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project versions follow [PEP 440](https://peps.python.org/pep-0440/).

## [0.4.5] - 2026-10-09

[Compare with 0.4.4](https://github.com/geozeke/vbart/compare/v0.4.4...v0.4.5)

### Removed

- Remove support for Python 3.10 (EOL) ([9392acb](https://github.com/geozeke/vbart/commit/9392acb9f3ea800a825a13c81c7968fb086b2619))

### Deployment & Operations

- Migrate type checker from mypy to pyrefly ([e1bc2ba](https://github.com/geozeke/vbart/commit/e1bc2ba8638e62b8ca265a6b19c9cd458f165881))
- Fix suppressed type errors ([59974ef](https://github.com/geozeke/vbart/commit/59974ef77764255bd9247686746949b0874b6a54))

## [0.4.4] - 2026-10-05

[Compare with 0.4.3](https://github.com/geozeke/vbart/compare/v0.4.3...v0.4.4)

### Deployment & Operations

- Lint git-cliff template ([9b18995](https://github.com/geozeke/vbart/commit/9b189956d07b4bc5a4e548c64d7e19438f2b7423))

### Dependencies

- *(deps-dev)* Bump ruff in the python-dependencies group ([7883530](https://github.com/geozeke/vbart/commit/7883530a9cace8813fc256a926046456ecd35867))
- *(deps-dev)* Bump ruff in the python-dependencies group ([863ff9e](https://github.com/geozeke/vbart/commit/863ff9e4c37417fd2241a755677f31b66f1a6a67))
- *(deps)* Bump astral-sh/setup-uv from 10.0.1 to 10.1.0 ([e2e419f](https://github.com/geozeke/vbart/commit/e2e419fabea0a8f248c19e20db2e67404720f61f))
- *(deps-dev)* Bump ruff in the python-dependencies group ([3bb15c7](https://github.com/geozeke/vbart/commit/3bb15c70a1f7ef6c43a9d61c8b033eb9114ee993))
- *(deps)* Bump astral-sh/setup-uv from 10.1.0 to 10.2.0 ([9e7e747](https://github.com/geozeke/vbart/commit/9e7e7473e808288ab6221b419b1544f4c95c98df))
- *(deps-dev)* Bump ruff ([689be6d](https://github.com/geozeke/vbart/commit/689be6d28706cd379d71847fd4270f68dd7db201))
- *(deps)* Bump urllib3 from 2.7.0 to 2.8.0 ([1176601](https://github.com/geozeke/vbart/commit/117660138f66c470a5e50c12805936feba354ad2))

## [0.4.3] - 2026-09-10

[Compare with 0.4.2](https://github.com/geozeke/vbart/compare/v0.4.2...v0.4.3)

### Deployment & Operations

- Fix stale reference in bump tooling ([5995acc](https://github.com/geozeke/vbart/commit/5995accd6097128772ba743fa74ab7a4bc66e2b8))

### Documentation

- Conduct documentation audit ([68402cf](https://github.com/geozeke/vbart/commit/68402cf7fd0d14a7ae2ad77ba9ba1871a35672f9))

### Dependencies

- *(deps-dev)* Bump mypy ([1973f5b](https://github.com/geozeke/vbart/commit/1973f5be4cb170ba9fa59acd0d1c6a832051fe9c))

## [0.4.2] - 2026-09-02

[Compare with 0.4.1](https://github.com/geozeke/vbart/compare/v0.4.1...v0.4.2)

### Fixed

- Fix broken release pipeline syntax ([0e80b97](https://github.com/geozeke/vbart/commit/0e80b97f5d746379b18f8e4d67cf081bacf1dd24))

## [0.4.1] - 2026-09-02

[Compare with 0.4.0](https://github.com/geozeke/vbart/compare/v0.4.0...v0.4.1)

### Deployment & Operations

- Upgrade dependency/release pipeline (#61) ([f72e3ae](https://github.com/geozeke/vbart/commit/f72e3aec9627c447054f88c5c7779803f3bffa15))

### Dependencies

- DEPS-See commit msg for list ([fa0acae](https://github.com/geozeke/vbart/commit/fa0acae231d85394d4ed5559c17d4234fe222fac))

## [0.4.0] - 2026-07-10

[View release tag](https://github.com/geozeke/vbart/releases/tag/v0.4.0)


### Added

- Support multiple compression tools (#58) (49a79da)

### Changed

- Support docker dependency >= 7.2.0 (3fdc0fd)
- Address pylance typing issues (49d8225)

### Dependencies

- DEPS-See commit msg for list (d77b606)
