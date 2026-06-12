"""Build dependency upgrade commit messages.

This module supports the ``just upgrade`` workflow by comparing locked
versions for first-order dependencies before and after an upgrade.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

COMMIT_SUBJECT = "deps: DEPS-See commit msg for list"
NAME_PATTERN = re.compile(r"^\s*([A-Za-z0-9_.-]+)")
OUTDATED_TREE_PATTERN = re.compile(
    r"^[\s│]*(?:[├└]── )?(?P<name>[A-Za-z0-9_.-]+)"
    r"(?:\[[^\]]+\])? v\S+ .*latest:"
)


@dataclass(frozen=True)
class DependencyUpdate:
    """A first-order dependency version change.

    Parameters
    ----------
    name
        The dependency name as declared in ``pyproject.toml``.
    old_version
        The dependency version before the upgrade.
    new_version
        The dependency version after the upgrade.
    """

    name: str
    old_version: str
    new_version: str


def normalize_name(name: str) -> str:
    """Normalize a Python distribution name.

    Parameters
    ----------
    name
        The distribution name to normalize.

    Returns
    -------
    str
        The normalized distribution name.
    """
    return re.sub(r"[-_.]+", "-", name).lower()


def dependency_name(requirement: str) -> str:
    """Extract the distribution name from a requirement string.

    Parameters
    ----------
    requirement
        A PEP 508 dependency string.

    Returns
    -------
    str
        The distribution name from the requirement.

    Raises
    ------
    ValueError
        If the requirement does not start with a distribution name.
    """
    match = NAME_PATTERN.match(requirement)
    if not match:
        msg = f"Could not parse dependency name from {requirement!r}"
        raise ValueError(msg)
    return match.group(1)


def first_order_dependencies(pyproject_path: Path) -> dict[str, str]:
    """Read direct dependency names from ``pyproject.toml``.

    Parameters
    ----------
    pyproject_path
        Path to the project metadata file.

    Returns
    -------
    dict[str, str]
        Normalized dependency names mapped to their declared names.
    """
    metadata = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    dependencies: dict[str, str] = {}

    for requirement in metadata.get("project", {}).get("dependencies", []):
        name = dependency_name(requirement)
        dependencies.setdefault(normalize_name(name), name)

    for group in metadata.get("dependency-groups", {}).values():
        for requirement in group:
            name = dependency_name(requirement)
            dependencies.setdefault(normalize_name(name), name)

    return dependencies


def locked_versions(lock_path: Path) -> dict[str, str]:
    """Read package versions from a uv lockfile.

    Parameters
    ----------
    lock_path
        Path to ``uv.lock``.

    Returns
    -------
    dict[str, str]
        Normalized package names mapped to locked versions.
    """
    lock_data = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    versions: dict[str, str] = {}
    for package in lock_data.get("package", []):
        name = package.get("name")
        version = package.get("version")
        source = package.get("source", {})
        if not name or not version or source.get("editable"):
            continue
        versions[normalize_name(name)] = version
    return versions


def dependency_updates(
    dependencies: dict[str, str],
    before_versions: dict[str, str],
    after_versions: dict[str, str],
) -> list[DependencyUpdate]:
    """Find changed first-order dependency versions.

    Parameters
    ----------
    dependencies
        Normalized first-order dependency names mapped to display names.
    before_versions
        Locked versions before the upgrade.
    after_versions
        Locked versions after the upgrade.

    Returns
    -------
    list[DependencyUpdate]
        Changed first-order dependency versions.
    """
    updates: list[DependencyUpdate] = []
    for normalized_name, display_name in dependencies.items():
        old_version = before_versions.get(normalized_name)
        new_version = after_versions.get(normalized_name)
        if old_version and new_version and old_version != new_version:
            updates.append(
                DependencyUpdate(
                    name=display_name,
                    old_version=old_version,
                    new_version=new_version,
                )
            )
    return updates


def render_commit_message(updates: list[DependencyUpdate]) -> str:
    """Render the dependency upgrade commit message.

    Parameters
    ----------
    updates
        Dependency version changes to include in the body.

    Returns
    -------
    str
        The complete commit message.
    """
    lines = [COMMIT_SUBJECT, ""]
    lines.extend(
        f"- {update.name}: {update.old_version} -> {update.new_version}"
        for update in updates
    )
    return "\n".join(lines) + "\n"


def outdated_first_order_packages(
    dependencies: dict[str, str],
    tree_output: str,
) -> list[str]:
    """Read outdated first-order package names from ``uv tree`` output.

    Parameters
    ----------
    dependencies
        Normalized first-order dependency names mapped to display names.
    tree_output
        Output from ``uv tree --outdated --depth=1``.

    Returns
    -------
    list[str]
        Outdated first-order package names to pass to ``uv sync
        --upgrade-package``.
    """
    packages: list[str] = []
    seen: set[str] = set()
    for line in tree_output.splitlines():
        match = OUTDATED_TREE_PATTERN.match(line)
        if not match:
            continue
        normalized_name = normalize_name(match.group("name"))
        if normalized_name not in dependencies or normalized_name in seen:
            continue
        seen.add(normalized_name)
        packages.append(dependencies[normalized_name])
    return packages


def _snapshot(args: argparse.Namespace) -> int:
    versions = locked_versions(args.lockfile)
    args.output.write_text(json.dumps(versions, indent=2) + "\n", encoding="utf-8")
    return 0


def _message(args: argparse.Namespace) -> int:
    dependencies = first_order_dependencies(args.pyproject)
    before_versions = json.loads(args.before.read_text(encoding="utf-8"))
    after_versions = locked_versions(args.lockfile)
    updates = dependency_updates(dependencies, before_versions, after_versions)

    if not updates:
        return 1

    args.output.write_text(render_commit_message(updates), encoding="utf-8")
    return 0


def _outdated(args: argparse.Namespace) -> int:
    dependencies = first_order_dependencies(args.pyproject)
    tree_output = sys.stdin.read()
    for package in outdated_first_order_packages(dependencies, tree_output):
        print(package)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    Returns
    -------
    argparse.ArgumentParser
        The configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Build dependency upgrade commit messages.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot = subparsers.add_parser("snapshot")
    snapshot.add_argument("--lockfile", type=Path, default=Path("uv.lock"))
    snapshot.add_argument("--output", type=Path, required=True)
    snapshot.set_defaults(func=_snapshot)

    message = subparsers.add_parser("message")
    message.add_argument("--pyproject", type=Path, default=Path("pyproject.toml"))
    message.add_argument("--lockfile", type=Path, default=Path("uv.lock"))
    message.add_argument("--before", type=Path, required=True)
    message.add_argument("--output", type=Path, required=True)
    message.set_defaults(func=_message)

    outdated = subparsers.add_parser("outdated")
    outdated.add_argument("--pyproject", type=Path, default=Path("pyproject.toml"))
    outdated.set_defaults(func=_outdated)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface.

    Parameters
    ----------
    argv
        Optional command-line arguments.

    Returns
    -------
    int
        Process exit code.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
