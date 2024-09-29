#!/usr/bin/env python3

"""Entry point for vbart."""

import argparse
import importlib
import shutil
import sys
from pathlib import Path
from types import ModuleType
from typing import List
from typing import Union

from vbart.constants import APP_NAME
from vbart.constants import ARG_PARSERS_BASE
from vbart.constants import VERSION

# ======================================================================


def collect_parsers(start: Path) -> List[str]:
    """Collect the module names of all argument parsers to import.

    Parameters
    ----------
    start : Path
        This the starting point (directory) for collection.

    Returns
    -------
    list[str]
        A list of argument parser module names.
    """
    parser_names: List[str] = []
    for p in start.iterdir():
        if p.is_file() and p.name != "__init__.py":
            parser_names.append(f"{APP_NAME}.parsers.{p.stem}")
    return parser_names


# ======================================================================


def main() -> None:
    """Get user input and perform backup and restore operations."""
    # Make sure docker is installed before going any further
    if not (shutil.which("docker")):
        print("\nYou must have docker installed to use vbart.\n")
        sys.exit(1)

    msg = """
    Volume Backup And Restoration Tool (for docker). A tool to easily
    backup and restore named docker volumes.
    """
    epi = f"Version: {VERSION}"
    parser = argparse.ArgumentParser(
        description=msg,
        epilog=epi,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{APP_NAME} {VERSION}",
    )
    msg = "For help on any command below, run: vbart {command} -h"
    subparsers = parser.add_subparsers(
        title="commands",
        dest="cmd",
        description=msg,
    )

    # Dynamically load argument subparsers.

    parser_names: List[str] = []
    parser_names = collect_parsers(ARG_PARSERS_BASE)
    parser_names.sort()

    # Argument parsers are saved in alphabetical order. This is a little
    # slight-of-hand to get the desired order presented on screen.
    parser_names[-1], parser_names[-2] = parser_names[-2], parser_names[-1]

    mod: Union[ModuleType, None] = None
    for p_name in parser_names:
        mod = importlib.import_module(p_name)
        mod.load_command_args(subparsers)

    # Run the selected command. Python's argparse module guarantees that
    # we'll get either: (1) a valid command or (2) no command at all
    # (args.cmd == None). Given that, we can easily determine the
    # entered command.

    args = parser.parse_args()
    if args.cmd:
        mod = importlib.import_module(f"{APP_NAME}.{args.cmd}")
    else:
        mod = importlib.import_module(f"{APP_NAME}.null")
    mod.task_runner(args)

    return


if __name__ == "__main__":
    main()
