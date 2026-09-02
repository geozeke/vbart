"""Validate release metadata and release notes for a pushed tag."""

from __future__ import annotations

import argparse
from pathlib import Path

from .changelog_tools import extract_release_notes
from .changelog_tools import parse_version
from .changelog_tools import project_version
from .changelog_tools import validate_changelog_collection

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Validate a tag and optionally write GitHub Actions outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    try:
        if not args.tag.startswith("v"):
            raise ValueError("Release tag must start with v")
        version = parse_version(args.tag[1:])
        project_version(ROOT, version.text)
        validate_changelog_collection(
            ROOT / "CHANGELOG.md", ROOT / "changelogs", version.text
        )
        extract_release_notes(args.tag, ROOT / "CHANGELOG.md", ROOT / "changelogs")
    except ValueError as exc:
        parser.error(str(exc))
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as handle:
            handle.write(
                f"version={version.text}\nprerelease={str(bool(version.prerelease)).lower()}\n"
            )


if __name__ == "__main__":
    main()
