# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

import subprocess as sp
import sys
from pathlib import Path

BASE = Path(__file__).parents[1]
CHANGELOG = BASE / "CHANGELOG.md"
PYPROJECT = BASE / "pyproject.toml"
UNRELEASED = BASE / "scratch" / "unreleased.md"


def main() -> None:

    # Check command line arguments
    if len(sys.argv) != 2:
        print("Invalid number of command line arguments")
        sys.exit(1)

    # Normalize the version number
    new_version = sys.argv[1].lower()
    if new_version[0] == "v":
        new_version = new_version[1:]

    # Generate updated changelog entry
    sp.run(
        f"git cliff -t {new_version} --unreleased -o scratch/unreleased.md".split(),
        capture_output=True,
    )

    # Reformat header
    with open(UNRELEASED, "r") as f:
        new_log = [line.rstrip() for line in f]
    header_parts = new_log[0].split()
    header_ver = header_parts[1].replace("[", "")
    header_ver = header_ver.replace("]", "")
    date = f"({header_parts[-1]})"
    new_log[0] = f"## {header_ver} {date} - latest"

    # Integrate it with the existing changelog
    with open(CHANGELOG, "r") as f:
        change_log = [line.rstrip() for line in f]
    for i in range(len(change_log)):
        if change_log[i].startswith("##") and change_log[i].endswith("latest"):
            change_log[i] = change_log[i][0 : change_log[i].index(")") + 1]
            break
    change_log = change_log[0:4] + new_log + change_log[1:]

    # Write-out the new changelog
    with open(CHANGELOG, "w") as f:
        f.write("\n".join(change_log) + "\n")

    # Bump version in pyproject.toml
    with open(PYPROJECT, "r") as f:
        pyproject = [line.rstrip() for line in f]
    for i in range(len(pyproject)):
        if pyproject[i].startswith("version"):
            pyproject[i] = f'version = "{new_version}"'
            break
    with open(PYPROJECT, "w") as f:
        f.write("\n".join(pyproject) + "\n")


if __name__ == "__main__":
    main()
