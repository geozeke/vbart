"""Tests for canonical changelog and release helper behavior."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.changelog_tools import extract_release_notes
from scripts.changelog_tools import parse_version
from scripts.changelog_tools import validate_changelog_collection
from scripts.changelog_tools import validate_commit_title

PREAMBLE = "# Changelog\n\nRelease history."


def release(version: str, category: str = "Changed") -> str:
    """Return one minimal canonical release section."""
    return f"## [{version}] - 2026-09-02\n\n### {category}\n\n- Release note."


@pytest.mark.parametrize("version", ("0.5.0", "0.5.0b1", "0.5.0rc1"))
def test_parse_version_accepts_canonical_pep440(version: str) -> None:
    """Canonical stable and prerelease versions are supported."""
    assert parse_version(version).text == version


@pytest.mark.parametrize("version", ("v0.5.0", "0.5.0-rc.1", "0.5", "00.5.0"))
def test_parse_version_rejects_legacy_forms(version: str) -> None:
    """Legacy version spellings fail closed."""
    with pytest.raises(ValueError, match="PEP 440"):
        parse_version(version)


def test_validate_commit_title_requires_supported_conventional_type() -> None:
    """PR-title validation accepts supported Conventional Commit types."""
    validate_commit_title("feat(release): add canonical changelog tooling")
    with pytest.raises(ValueError, match="Conventional"):
        validate_commit_title("Add canonical changelog tooling")


def test_changelog_validation_rejects_legacy_categories(tmp_path: Path) -> None:
    """Only banip-style canonical categories are accepted."""
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        f"{PREAMBLE}\n\n{release('0.5.0', '🚀 Features')}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Unsupported"):
        validate_changelog_collection(changelog, tmp_path / "changelogs")


def test_release_notes_are_extracted_from_matching_archive(tmp_path: Path) -> None:
    """Archived releases produce a body without their release heading."""
    changelog = tmp_path / "CHANGELOG.md"
    archives = tmp_path / "changelogs"
    archives.mkdir()
    changelog.write_text(f"{PREAMBLE}\n\n{release('0.5.0')}\n", encoding="utf-8")
    archive = archives / "v0.4.x.md"
    archive.write_text(
        "# Changelog archive: 0.4.x\n\nArchive.\n\n" + release("0.4.0") + "\n",
        encoding="utf-8",
    )
    notes = extract_release_notes("v0.4.0", changelog, archives)
    assert notes == "### Changed\n\n- Release note.\n"
