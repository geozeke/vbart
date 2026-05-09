from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "archive_changelog.py"
SPEC = importlib.util.spec_from_file_location("archive_changelog", SCRIPT_PATH)
assert SPEC is not None
archive_changelog = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = archive_changelog
SPEC.loader.exec_module(archive_changelog)


def test_patch_bump_does_not_archive_existing_old_sections(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    archive_dir = tmp_path / "changelogs"
    original = """## 0.3.2 (2026-05-09)

### Fixed

- Patch release.

## 0.3.1 (2026-05-08)

### Fixed

- Previous patch.

## 0.2.1 (2026-03-27)

### Changed

- Older minor entry.

"""
    changelog.write_text(original, encoding="utf-8")

    changed = archive_changelog.archive_changelog("v0.3.2", changelog, archive_dir)

    assert not changed
    assert changelog.read_text(encoding="utf-8") == original
    assert not archive_dir.exists()


def test_minor_bump_archives_old_sections_and_moves_links(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    archive_dir = tmp_path / "changelogs"
    changelog.write_text(
        """## 0.4.0 (2026-05-09)

### Added

- Current minor entry.

## 0.3.1 (2026-05-08)

### Fixed

- Previous minor entry.

## 0.2.1 (2026-03-27)

### Changed

- Older linked entry using [pkg][pkg].

[pkg]: https://example.test/pkg
""",
        encoding="utf-8",
    )

    changed = archive_changelog.archive_changelog("0.4.0", changelog, archive_dir)

    assert changed
    active = changelog.read_text(encoding="utf-8")
    assert "## 0.4.0" in active
    assert "## 0.3.1" not in active
    assert "[pkg]:" not in active

    archive_03 = (archive_dir / "v0.3.x.md").read_text(encoding="utf-8")
    assert "## 0.3.1" in archive_03

    archive_02 = (archive_dir / "v0.2.x.md").read_text(encoding="utf-8")
    assert "## 0.2.1 (2026-03-27)" in archive_02
    assert "[pkg]: https://example.test/pkg" in archive_02


def test_major_bump_archives_previous_major_line(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    archive_dir = tmp_path / "changelogs"
    changelog.write_text(
        """## 1.0.0 (2026-05-09)

### Added

- New major.

## 0.3.1 (2026-05-08)

### Fixed

- Previous major.
""",
        encoding="utf-8",
    )

    changed = archive_changelog.archive_changelog("1.0.0", changelog, archive_dir)

    assert changed
    assert "## 1.0.0" in changelog.read_text(encoding="utf-8")
    assert "## 0.3.1" in (archive_dir / "v0.3.x.md").read_text(encoding="utf-8")


def test_force_archives_for_initial_cleanup(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    archive_dir = tmp_path / "changelogs"
    changelog.write_text(
        """## 0.3.1 (2026-05-08)

### Fixed

- Current patch.

## 0.3.0 (2026-04-24)

### Changed

- Current minor patch.

## 0.2.1 (2026-03-27)

### Added

- Previous minor.
""",
        encoding="utf-8",
    )

    changed = archive_changelog.archive_changelog(
        "0.3.1",
        changelog,
        archive_dir,
        force=True,
    )

    assert changed
    active = changelog.read_text(encoding="utf-8")
    assert "## 0.3.1" in active
    assert "## 0.3.0" in active
    assert "## 0.2.1" not in active
    assert "## 0.2.1" in (archive_dir / "v0.2.x.md").read_text(encoding="utf-8")


def test_archive_merges_existing_sections_newest_first(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    archive_dir = tmp_path / "changelogs"
    archive_dir.mkdir()
    changelog.write_text(
        """## 0.4.0 (2026-05-09)

### Added

- Current release.

## 0.3.1 (2026-05-08)

### Fixed

- New archived release.
""",
        encoding="utf-8",
    )
    (archive_dir / "v0.3.x.md").write_text(
        """## 0.3.0 (2026-04-24)

### Added

- Existing archived release.
""",
        encoding="utf-8",
    )

    archive_changelog.archive_changelog("0.4.0", changelog, archive_dir)

    archive = (archive_dir / "v0.3.x.md").read_text(encoding="utf-8")
    assert archive.index("## 0.3.1") < archive.index("## 0.3.0")


def test_extract_release_notes_reads_active_release(tmp_path: Path) -> None:
    output = run_extract_release_notes(
        tmp_path,
        "v0.3.1",
        changelog="""## 0.3.1 (2026-05-08)

### Fixed

- Active release.
""",
    )

    assert "## 0.3.1" in output
    assert "Active release." in output


def test_extract_release_notes_reads_archived_release(tmp_path: Path) -> None:
    output = run_extract_release_notes(
        tmp_path,
        "v0.1.9",
        changelog="""## 0.3.1 (2026-05-08)

### Fixed

- Active release.
""",
        archive="""## 0.1.9 (2026-01-09)

### Changed

- Archived release.
""",
        archive_name="v0.1.x.md",
    )

    assert "## 0.1.9 (2026-01-09)" in output
    assert "Archived release." in output


def test_extract_release_notes_keeps_non_release_level_two_headings(
    tmp_path: Path,
) -> None:
    output = run_extract_release_notes(
        tmp_path,
        "v0.2.0",
        changelog="""## 0.3.1 (2026-05-08)

### Fixed

- Active release.
""",
        archive="""## 0.2.0 (2026-03-06)

## BREAKING

- Breaking change.

### Fixed

- Archived fix.
""",
    )

    assert "## BREAKING" in output
    assert "Archived fix." in output


def test_extract_release_notes_reports_missing_release(tmp_path: Path) -> None:
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    source_script = Path(__file__).resolve().parents[1] / "scripts"
    script = scripts_dir / "extract_release_notes.sh"
    script.write_text(
        (source_script / "extract_release_notes.sh").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text(
        "## 0.3.1 (2026-05-08)\n\n- Active release.\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["sh", str(script), "v0.2.0", str(tmp_path / "release.md")],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "not found in CHANGELOG.md or" in result.stderr


def run_extract_release_notes(
    tmp_path: Path,
    tag: str,
    changelog: str,
    archive: str | None = None,
    archive_name: str = "v0.2.x.md",
) -> str:
    """Run release-note extraction against a temporary project."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    archive_dir = tmp_path / "changelogs"
    archive_dir.mkdir()
    source_script = Path(__file__).resolve().parents[1] / "scripts"
    script = scripts_dir / "extract_release_notes.sh"
    script.write_text(
        (source_script / "extract_release_notes.sh").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
    if archive:
        (archive_dir / archive_name).write_text(archive, encoding="utf-8")
    output = tmp_path / "release.md"

    subprocess.run(
        ["sh", str(script), tag, str(output)],
        check=True,
        capture_output=True,
        text=True,
    )
    return output.read_text(encoding="utf-8")
