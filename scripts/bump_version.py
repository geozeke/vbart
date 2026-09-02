"""Prepare a canonical vbart release version and changelog section."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from .changelog_tools import Section
from .changelog_tools import archive_changelog
from .changelog_tools import format_changelog
from .changelog_tools import parse_version
from .changelog_tools import project_version
from .changelog_tools import split_changelog
from .changelog_tools import validate_changelog_collection
from .changelog_tools import validate_commit_title

ROOT = Path(__file__).resolve().parents[1]
CONVENTIONAL_BASELINE = "0795b5537486cfb13b3b2054309d5817dfcbcbc1"


def run(*args: str, capture: bool = False) -> str:
    """Run a command from the project root.

    Parameters
    ----------
    *args
        Command and arguments to execute.
    capture
        Whether to return standard output.

    Returns
    -------
    str
        Captured standard output, or an empty string.
    """
    result = subprocess.run(
        args, cwd=ROOT, check=True, text=True, capture_output=capture
    )
    return result.stdout if capture else ""


def validate_release_commits() -> None:
    """Require Conventional Commit subjects since the migration baseline.

    Raises
    ------
    ValueError
        If a non-merge commit has an unsupported title.
    """
    subjects = run(
        "git",
        "log",
        f"{CONVENTIONAL_BASELINE}..HEAD",
        "--no-merges",
        "--format=%s",
        capture=True,
    )
    for subject in subjects.splitlines():
        try:
            validate_commit_title(subject)
        except ValueError as exc:
            raise ValueError(f"Invalid release commit title: {subject}") from exc


def bump(version_text: str) -> None:
    """Generate notes, update metadata, and archive inactive release lines.

    Parameters
    ----------
    version_text
        Canonical PEP 440 release version.

    Raises
    ------
    ValueError
        If release prerequisites or generated metadata are invalid.
    subprocess.CalledProcessError
        If an external release command fails.
    """
    target = parse_version(version_text)
    if run("git", "status", "--porcelain=v1", "--untracked-files=all", capture=True):
        raise ValueError("Working tree must be clean before preparing a release")
    if shutil.which("git-cliff") is None:
        raise ValueError("git-cliff is required to prepare a release")
    validate_release_commits()
    current = parse_version(project_version(ROOT))
    tags = run("git", "tag", "--list", f"v{target.text}", capture=True)
    if target.sort_key() <= current.sort_key() and tags.strip():
        raise ValueError("Target version must be newer than the current tagged version")
    generated = run(
        "git-cliff", "--unreleased", "--tag", f"v{target.text}", capture=True
    )
    preamble, generated_sections = split_changelog(generated)
    if len(generated_sections) != 1 or generated_sections[0].label != target.text:
        raise ValueError("git-cliff did not produce the requested release section")
    existing_preamble, existing_sections = split_changelog(
        (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    )
    release = generated_sections[0]
    unreleased = next(
        (item for item in existing_sections if item.label == "Unreleased"), None
    )
    if unreleased is not None:
        release = Section(
            release.label,
            f"{release.text}\n\n" + "\n".join(unreleased.text.splitlines()[1:]).strip(),
        )
    retained = [
        item
        for item in existing_sections
        if item.label not in {"Unreleased", target.text}
    ]
    snapshots = {
        path: path.read_bytes() if path.exists() else None
        for path in [ROOT / "pyproject.toml", ROOT / "uv.lock", ROOT / "CHANGELOG.md"]
    }
    archives = ROOT / "changelogs"
    archive_snapshots = {path: path.read_bytes() for path in archives.glob("*.md")}
    try:
        run("uv", "version", target.text, "--no-sync")
        (ROOT / "CHANGELOG.md").write_text(
            format_changelog(preamble or existing_preamble, [release, *retained]),
            encoding="utf-8",
        )
        archive_changelog(target.text, ROOT / "CHANGELOG.md", archives)
        project_version(ROOT, target.text)
        validate_changelog_collection(ROOT / "CHANGELOG.md", archives, target.text)
    except Exception:
        for path, content in snapshots.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        for path in archives.glob("*.md"):
            if path not in archive_snapshots:
                path.unlink()
        for path, content in archive_snapshots.items():
            path.write_bytes(content)
        raise


def main() -> None:
    """Parse and prepare a target version.

    Raises
    ------
    SystemExit
        If command-line validation or release preparation fails.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Canonical PEP 440 version, such as 0.5.0rc1.")
    args = parser.parse_args()
    try:
        bump(args.version)
    except (ValueError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
