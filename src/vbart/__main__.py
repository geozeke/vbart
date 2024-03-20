#!/usr/bin/env python3

"""Entry point for vbart."""

import argparse
import importlib
import shutil
import sys
from pathlib import Path
from types import ModuleType

from vbart.constants import ARG_PARSERS_BASE

# ======================================================================


def collect_modules(start: Path) -> list[str]:
    """Collect the names of all modules to import.

    Parameters
    ----------
    start : Path
        This the starting point (directory) for collection.

    Returns
    -------
    list[str]
        A list of module names.
    """
    mod_names: list[str] = []
    for p in start.iterdir():
        if p.is_file() and p.name != "__init__.py":
            if "plugins" in str(p):
                prefix = "plugins.parsers"
            else:
                prefix = "parsers"
            mod_names.append(f"{prefix}.{p.stem}")
    return mod_names


# ======================================================================


def main() -> None:
    """Get user input and perform backup and restore operations."""
    # Make sure docker is installed before going any further
    if not (shutil.which("docker")):
        print("\nYou must have docker installed to use vbart.\n")
        sys.exit(1)

    msg = """A utility to easily backup and restore named docker
    volumes. For help on any command below, use: vbart {command} -h"""
    epi = "Version: 0.1.0"
    parser = argparse.ArgumentParser(
        description=msg,
        epilog=epi,
    )
    subparsers = parser.add_subparsers(title="commands", dest="cmd")

    # Dynamically load argument subparsers.

    mod_names: list[str] = []
    mod: ModuleType | None = None
    mod_names = collect_modules(ARG_PARSERS_BASE)
    mod_names.sort()

    # Argument parsers are saved in alphabetical order. This is a little
    # slight-of-hand to get the the desired order presented on screen.
    mod_names[-1], mod_names[-2] = mod_names[-2], mod_names[-1]

    for mod_name in mod_names:
        mod = importlib.import_module(mod_name)
        mod.load_command_args(subparsers)

    args = parser.parse_args()
    match (args.cmd):
        case "backup":
            mod = importlib.import_module("vbart.backup")
        case "backups":
            mod = importlib.import_module("vbart.backups")
        case "restore":
            mod = importlib.import_module("vbart.restore")
        case "refresh":
            mod = importlib.import_module("vbart.refresh")
        case _:
            mod = importlib.import_module("vbart.null")
    mod.task_runner(args)

    return


if __name__ == "__main__":
    main()
