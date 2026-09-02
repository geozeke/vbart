"""Extract one release's notes from the canonical changelog collection."""

from __future__ import annotations

import argparse
from pathlib import Path

from .changelog_tools import extract_release_notes

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Write the requested release notes to the output path.

    Raises
    ------
    SystemExit
        If the tag has no valid release notes.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        notes = extract_release_notes(
            args.tag, ROOT / "CHANGELOG.md", ROOT / "changelogs"
        )
    except ValueError as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(notes, encoding="utf-8")


if __name__ == "__main__":
    main()
