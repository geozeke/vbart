"""Provide canonical changelog and Conventional Commit helpers."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

VERSION_RE = re.compile(
    r"^(?P<version>(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:(?:a|b|rc)(?:0|[1-9]\d*))?)$"
)
HEADING_RE = re.compile(
    r"^## \[(?P<label>Unreleased|.+)\](?: - (?P<date>\d{4}-\d{2}-\d{2}))?$"
)
GROUP_RE = re.compile(r"^### (?P<group>.+)$")
TITLE_RE = re.compile(
    r"^(?:feat|change|deprecate|remove|fix|security|perf|deploy|docs|build|chore|ci|refactor|style|test|revert)(?:\([a-z0-9][a-z0-9._/-]*\))?!?: [^\s].*$"
)
GROUPS = (
    "Breaking Changes",
    "Security",
    "Added",
    "Changed",
    "Deprecated",
    "Removed",
    "Fixed",
    "Performance",
    "Deployment & Operations",
    "Documentation",
    "Dependencies",
    "Reverted",
)


@dataclass(frozen=True)
class Version:
    """Represent a canonical PEP 440 project version."""

    text: str
    major: int
    minor: int
    patch: int
    prerelease: str

    @property
    def major_minor(self) -> tuple[int, int]:
        """Return the major and minor release line."""
        return self.major, self.minor

    def sort_key(self) -> tuple[int, int, int, int, int]:
        """Return a release ordering key."""
        if not self.prerelease:
            return self.major, self.minor, self.patch, 3, 0
        match = re.fullmatch(r"(a|b|rc)(\d+)", self.prerelease)
        assert match is not None
        rank = {"a": 0, "b": 1, "rc": 2}[match.group(1)]
        return self.major, self.minor, self.patch, rank, int(match.group(2))


@dataclass(frozen=True)
class Section:
    """Represent one canonical changelog section."""

    label: str
    text: str

    @property
    def version(self) -> Version | None:
        """Return the section version, if this is a release."""
        return None if self.label == "Unreleased" else parse_version(self.label)


def parse_version(text: str) -> Version:
    """Parse a canonical PEP 440 version without a leading ``v``."""
    match = VERSION_RE.fullmatch(text)
    if match is None:
        raise ValueError(f"Expected canonical PEP 440 version, got: {text}")
    version = match.group("version")
    core, *suffix = re.split(r"(?=[a-z])", version)
    major, minor, patch = (int(part) for part in core.split("."))
    return Version(version, major, minor, patch, suffix[0] if suffix else "")


def split_changelog(text: str) -> tuple[str, list[Section]]:
    """Split canonical changelog text into a preamble and sections."""
    lines = text.splitlines()
    starts = [index for index, line in enumerate(lines) if HEADING_RE.fullmatch(line)]
    if not starts:
        return text.strip(), []
    sections = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        match = HEADING_RE.fullmatch(lines[start])
        assert match is not None
        sections.append(
            Section(match.group("label"), "\n".join(lines[start:end]).strip())
        )
    return "\n".join(lines[: starts[0]]).strip(), sections


def format_changelog(preamble: str, sections: list[Section]) -> str:
    """Return normalized changelog text."""
    return (
        "\n\n".join(
            [preamble.strip(), *(item.text.strip() for item in sections)]
        ).strip()
        + "\n"
    )


def validate_commit_title(title: str) -> None:
    """Require a supported Conventional Commit title."""
    if not TITLE_RE.fullmatch(title):
        raise ValueError("Expected a supported Conventional Commit title")


def project_version(root: Path, expected: str | None = None) -> str:
    """Require matching project and lockfile versions."""
    with (root / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)
    with (root / "uv.lock").open("rb") as handle:
        lock = tomllib.load(handle)
    project = str(pyproject["project"]["version"])
    package = next((item for item in lock["package"] if item["name"] == "vbart"), None)
    if package is None or str(package["version"]) != project:
        raise ValueError("Project versions are not synchronized")
    parse_version(project)
    if expected is not None and project != parse_version(expected).text:
        raise ValueError(f"Project version {project} does not match {expected}")
    return project


def validate_changelog_collection(
    changelog: Path, archives: Path, expected: str | None = None
) -> None:
    """Validate active and archived changelogs use only the current format."""
    seen: set[str] = set()
    for path in [changelog, *sorted(archives.glob("v*.x.md"))]:
        preamble, sections = split_changelog(path.read_text(encoding="utf-8"))
        if not preamble.startswith("# Changelog") or not sections:
            raise ValueError(f"{path} is not a canonical changelog")
        versions = [section.version for section in sections]
        if any(version is None for version in versions):
            raise ValueError("Unreleased sections cannot be archived or released")
        parsed = [version for version in versions if version is not None]
        if parsed != sorted(parsed, key=Version.sort_key, reverse=True):
            raise ValueError(f"{path} releases are not newest first")
        for section, version in zip(sections, parsed, strict=True):
            match = HEADING_RE.fullmatch(section.text.splitlines()[0])
            if match is None or not match.group("date"):
                raise ValueError(f"{section.label} is missing a canonical date")
            if section.label in seen:
                raise ValueError(f"Duplicate changelog section: {section.label}")
            seen.add(section.label)
            groups = [
                match.group("group")
                for line in section.text.splitlines()
                if (match := GROUP_RE.fullmatch(line))
            ]
            if any(group not in GROUPS for group in groups):
                raise ValueError("Unsupported changelog heading")
            if groups != sorted(groups, key=GROUPS.index):
                raise ValueError("Changelog headings are out of order")
            if (
                path != changelog
                and path.name != f"v{version.major}.{version.minor}.x.md"
            ):
                raise ValueError(f"{section.label} belongs in a different archive")
    if expected and expected not in seen:
        raise ValueError(f"Changelog section for {expected} was not found")


def archive_changelog(version: str, changelog: Path, archives: Path) -> None:
    """Archive release sections outside ``version``'s minor line."""
    target = parse_version(version)
    preamble, sections = split_changelog(changelog.read_text(encoding="utf-8"))
    active: list[Section] = []
    moved: dict[tuple[int, int], list[Section]] = {}
    for section in sections:
        parsed = section.version
        if parsed is None or parsed.major_minor == target.major_minor:
            active.append(section)
        else:
            moved.setdefault(parsed.major_minor, []).append(section)
    for minor, sections_to_move in moved.items():
        path = archives / f"v{minor[0]}.{minor[1]}.x.md"
        existing = (
            split_changelog(path.read_text(encoding="utf-8"))[1]
            if path.exists()
            else []
        )
        merged = {section.label: section for section in [*existing, *sections_to_move]}
        ordered = sorted(
            merged.values(),
            key=lambda item: (
                item.version.sort_key() if item.version else (0, 0, 0, 0, 0)
            ),
            reverse=True,
        )
        archive_preamble = f"# Changelog archive: {minor[0]}.{minor[1]}.x\n\nArchived vbart releases for the {minor[0]}.{minor[1]}.x minor version line."
        path.write_text(format_changelog(archive_preamble, ordered), encoding="utf-8")
    changelog.write_text(format_changelog(preamble, active), encoding="utf-8")


def extract_release_notes(tag: str, changelog: Path, archives: Path) -> str:
    """Return the body of a release section selected by its ``v`` tag."""
    if not tag.startswith("v"):
        raise ValueError("Release tag must start with v")
    version = parse_version(tag[1:])
    paths = [changelog, archives / f"v{version.major}.{version.minor}.x.md"]
    matches = [
        section
        for path in paths
        if path.exists()
        for section in split_changelog(path.read_text(encoding="utf-8"))[1]
        if section.label == version.text
    ]
    if len(matches) != 1:
        raise ValueError(f"Release notes for {version.text} were not found uniquely")
    notes = "\n".join(matches[0].text.splitlines()[1:]).strip()
    if not notes:
        raise ValueError("Release notes are empty")
    return notes + "\n"
