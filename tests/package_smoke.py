"""Smoke-test an installed vbart distribution artifact."""

from __future__ import annotations

import subprocess
from importlib.metadata import version

import vbart
import vbart.app


def main() -> None:
    """Verify imports, installed metadata, and console entry points."""
    package_version = version("vbart")
    assert vbart.__file__
    assert vbart.app.__file__
    result = subprocess.run(
        ("vbart", "--version"), check=True, capture_output=True, text=True
    )
    assert result.stdout.strip() == f"vbart {package_version}"
    result = subprocess.run(
        ("vbart", "--help"), check=True, capture_output=True, text=True
    )
    assert "usage: vbart" in result.stdout


if __name__ == "__main__":
    main()
