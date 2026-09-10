"""Tests for canonical changelog and release helper behavior."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import bump_version
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


def test_release_commit_validation_uses_latest_reachable_version_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only commits since the newest reachable release are validated."""
    calls: list[tuple[str, ...]] = []

    def fake_run(*args: str, capture: bool = False) -> str:
        """Return Git output for the release-validation commands."""
        assert capture
        calls.append(args)
        if args[:3] == ("git", "tag", "--merged"):
            return "v0.4.1\nv0.4.2\nlatest\n"
        if args[:2] == ("git", "log"):
            return "docs: document release workflow\n"
        raise AssertionError(f"Unexpected command: {args}")

    monkeypatch.setattr(bump_version, "run", fake_run)

    bump_version.validate_release_commits()

    assert calls[1] == (
        "git",
        "log",
        "v0.4.2..HEAD",
        "--no-merges",
        "--format=%s",
    )


def test_latest_release_tag_requires_reachable_version_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Release preparation fails clearly without a reachable version tag."""
    monkeypatch.setattr(bump_version, "run", lambda *args, **kwargs: "latest\n")

    with pytest.raises(ValueError, match="No reachable canonical version tag"):
        bump_version.latest_release_tag()


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
