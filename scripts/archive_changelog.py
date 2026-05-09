#!/usr/bin/env python3
"""Archive old minor-version changelog entries.

Functions
---------
main
    Parse command-line arguments and archive stale changelog sections.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


HEADING_RE = re.compile(
    r"^##\s+v?(?P<version>\d+\.\d+\.\d+)\s+\(\d{4}-\d{2}-\d{2}\)$"
)
LINK_DEFINITION_RE = re.compile(r"^\[([^\]]+)\]:\s+\S+", re.MULTILINE)
REFERENCE_RE = re.compile(r"\[([^\]\n]+)\](?:\[([^\]\n]+)\])?")


@dataclass(frozen=True)
class ReleaseSection:
    """Represent one release section from a changelog.

    Parameters
    ----------
    version
        Semantic version for the release, without a leading ``v``.
    text
        Full Markdown text for the section.
    """

    version: str
    text: str

    @property
    def major_minor(self) -> tuple[int, int]:
        """Return the semantic major/minor version tuple."""
        major, minor, _patch = parse_version(self.version)
        return major, minor


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse a semantic version.

    Parameters
    ----------
    version
        Semantic version with or without a leading ``v``.

    Returns
    -------
    tuple[int, int, int]
        Major, minor, and patch components.

    Raises
    ------
    ValueError
        If ``version`` is not a three-part semantic version.
    """
    normalized = version.removeprefix("v")
    parts = normalized.split(".")
    if len(parts) != 3:
        raise ValueError(f"Expected semantic version, got: {version}")
    try:
        major, minor, patch = (int(part) for part in parts)
    except ValueError as exc:
        raise ValueError(f"Expected semantic version, got: {version}") from exc
    return major, minor, patch


def split_changelog(text: str) -> tuple[str, list[ReleaseSection], dict[str, str]]:
    """Split changelog text into preamble, releases, and link definitions.

    Parameters
    ----------
    text
        Full changelog Markdown content.

    Returns
    -------
    tuple[str, list[ReleaseSection], dict[str, str]]
        Preamble text, release sections, and link reference definitions keyed
        by label.
    """
    lines = text.splitlines()
    link_definitions: dict[str, str] = {}
    content_lines: list[str] = []

    for line in lines:
        link_match = LINK_DEFINITION_RE.match(line)
        if link_match:
            link_definitions[link_match.group(1)] = line
        else:
            content_lines.append(line)

    heading_indexes: list[tuple[int, re.Match[str]]] = []
    for index, line in enumerate(content_lines):
        match = HEADING_RE.match(line)
        if match:
            heading_indexes.append((index, match))

    if not heading_indexes:
        return "\n".join(content_lines).strip(), [], link_definitions

    first_heading_index = heading_indexes[0][0]
    preamble = "\n".join(content_lines[:first_heading_index]).strip()
    releases: list[ReleaseSection] = []

    for heading_position, (start, match) in enumerate(heading_indexes):
        if heading_position + 1 < len(heading_indexes):
            end = heading_indexes[heading_position + 1][0]
        else:
            end = len(content_lines)
        section = "\n".join(content_lines[start:end]).strip()
        releases.append(ReleaseSection(match.group("version"), section))

    return preamble, releases, link_definitions


def section_sort_key(section: ReleaseSection) -> tuple[int, int, int]:
    """Return a semantic-version sort key for a release section."""
    return parse_version(section.version)


def find_used_references(text: str) -> set[str]:
    """Find Markdown reference labels used by ``text``."""
    labels: set[str] = set()
    for match in REFERENCE_RE.finditer(text):
        label = match.group(2) or match.group(1)
        if label and not label.startswith("http"):
            labels.add(label)
    return labels


def format_changelog(
    preamble: str,
    releases: list[ReleaseSection],
    link_definitions: dict[str, str],
) -> str:
    """Format changelog parts as Markdown text.

    Parameters
    ----------
    preamble
        Text before the first release heading.
    releases
        Release sections to include in newest-first order.
    link_definitions
        Available link reference definitions.

    Returns
    -------
    str
        Complete changelog Markdown.
    """
    parts: list[str] = []
    if preamble:
        parts.append(preamble)
    parts.extend(section.text.strip() for section in releases)

    body = "\n\n".join(part for part in parts if part).strip()
    used_references = find_used_references(body)
    references = [
        link_definitions[label]
        for label in link_definitions
        if label in used_references
    ]
    if references:
        body = f"{body}\n\n" + "\n".join(references)
    return f"{body}\n"


def should_archive(
    target_minor: tuple[int, int],
    releases: list[ReleaseSection],
    force: bool,
) -> bool:
    """Return whether this run should archive non-target sections.

    Parameters
    ----------
    target_minor
        Major/minor line for the target release.
    releases
        Parsed releases from the active changelog.
    force
        Whether to archive even when the second release is still in the
        target major/minor line.

    Returns
    -------
    bool
        ``True`` when archive cleanup should run.
    """
    if force:
        return True
    if len(releases) < 2:
        return False
    return releases[1].major_minor != target_minor


def archive_changelog(
    version: str,
    changelog_path: Path,
    archive_dir: Path,
    force: bool = False,
) -> bool:
    """Archive changelog sections outside ``version``'s major/minor line.

    Parameters
    ----------
    version
        Target semantic version, with or without a leading ``v``.
    changelog_path
        Path to the active changelog file.
    archive_dir
        Directory that stores minor-line archive files.
    force
        Archive any non-target minor line even during a patch update.

    Returns
    -------
    bool
        ``True`` when files were updated, otherwise ``False``.
    """
    target_minor = parse_version(version)[:2]
    preamble, releases, link_definitions = split_changelog(
        changelog_path.read_text(encoding="utf-8")
    )
    if not should_archive(target_minor, releases, force):
        return False

    active_releases: list[ReleaseSection] = []
    archived_by_minor: dict[tuple[int, int], list[ReleaseSection]] = {}

    for release in releases:
        if release.major_minor == target_minor:
            active_releases.append(release)
        else:
            archived_by_minor.setdefault(release.major_minor, []).append(release)

    if not archived_by_minor:
        return False

    archive_dir.mkdir(parents=True, exist_ok=True)
    for major_minor, archived_releases in archived_by_minor.items():
        archive_path = archive_dir / f"v{major_minor[0]}.{major_minor[1]}.x.md"
        existing_preamble = ""
        existing_releases: list[ReleaseSection] = []
        existing_links: dict[str, str] = {}
        if archive_path.exists():
            existing_preamble, existing_releases, existing_links = split_changelog(
                archive_path.read_text(encoding="utf-8")
            )

        merged_sections = {section.version: section for section in existing_releases}
        merged_sections.update({section.version: section for section in archived_releases})
        merged_releases = sorted(
            merged_sections.values(),
            key=section_sort_key,
            reverse=True,
        )
        archive_links = existing_links | link_definitions
        archive_path.write_text(
            format_changelog(existing_preamble, merged_releases, archive_links),
            encoding="utf-8",
        )

    changelog_path.write_text(
        format_changelog(preamble, active_releases, link_definitions),
        encoding="utf-8",
    )
    return True


def main() -> None:
    """Run the changelog archiver from the command line."""
    parser = argparse.ArgumentParser(
        description="Archive CHANGELOG.md entries outside a semantic minor line."
    )
    parser.add_argument("version", help="Target semantic version, e.g. v0.4.0.")
    parser.add_argument(
        "--changelog",
        type=Path,
        default=Path("CHANGELOG.md"),
        help="Path to the active changelog.",
    )
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=Path("changelogs"),
        help="Directory for archived minor-version changelogs.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Archive non-target minor lines even during a patch update.",
    )
    args = parser.parse_args()
    archive_changelog(args.version, args.changelog, args.archive_dir, args.force)


if __name__ == "__main__":
    main()
